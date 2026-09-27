"""Dataset de evaluación del agente (T031).

Casos curados `pregunta -> expectativa` según `docs/quality/evaluation.md`, cubriendo:
- ruta SQL (datos), en español e inglés;
- ruta RAG (reglas/ideas), en español e inglés, con cita de fuente;
- ruta AMBAS (mixta);
- casos de rehúso (sin datos / fuera de los documentos / pedidos de escritura).

Cada caso trae lo necesario para verificar automáticamente: ruta esperada, y según la categoría
un `gold_sql` (para comparar el dato), la fuente esperada (RAG) o `must_refuse`.

Nota: los casos RAG dependen de los PDFs de muestra actuales; si se reemplazan por los reales,
revisar `expect_source` y las preguntas.
"""

from __future__ import annotations

from dataclasses import dataclass

from chess_agent.db import client
from chess_agent.state import AgentState


@dataclass(frozen=True)
class EvalCase:
    id: str
    pregunta: str
    idioma: str  # es | en
    ruta_esperada: str  # SQL | RAG | AMBAS
    categoria: str  # sql | rag | refusal | mixta
    gold_sql: str | None = None  # consulta de referencia (verificación SQL)
    expect_source: str | None = None  # substring del PDF esperado (RAG)
    must_refuse: bool = False


CASES: list[EvalCase] = [
    # --- SQL (español) ---
    EvalCase("sql-carlsen-white", "¿Cuántas partidas ganó Carlsen con blancas?", "es", "SQL",
             "sql",
             gold_sql="SELECT COUNT(*) FROM games g JOIN players p ON g.white_player_id=p.player_id"
                      " WHERE p.name ILIKE '%Carlsen%' AND g.result='1-0'"),
    EvalCase("sql-top5", "¿Cuáles son los 5 jugadores con mayor peak rating?", "es", "SQL", "sql",
             gold_sql="SELECT name FROM players ORDER BY peak_rating DESC NULLS LAST LIMIT 5"),
    EvalCase("sql-draws", "¿Cuántas partidas terminaron en tablas?", "es", "SQL", "sql",
             gold_sql="SELECT COUNT(*) FROM games WHERE result='1/2-1/2'"),
    EvalCase("sql-avg-norway", "¿Cuál es el rating promedio de los jugadores de Noruega?", "es",
             "SQL", "sql",
             gold_sql="SELECT round(avg(peak_rating)) FROM players WHERE country='Norway'"),
    EvalCase("sql-gm", "¿Qué jugadores tienen título de Gran Maestro?", "es", "SQL", "sql",
             gold_sql="SELECT name FROM players WHERE title='GM' ORDER BY name"),
    # --- SQL (inglés) ---
    EvalCase("sql-draws-en", "how many draws are there?", "en", "SQL", "sql",
             gold_sql="SELECT COUNT(*) FROM games WHERE result='1/2-1/2'"),
    EvalCase("sql-carlsen-white-en", "how many games did Carlsen win with white?", "en", "SQL",
             "sql",
             gold_sql="SELECT COUNT(*) FROM games g JOIN players p ON g.white_player_id=p.player_id"
                      " WHERE p.name ILIKE '%Carlsen%' AND g.result='1-0'"),
    # --- RAG (español) ---
    EvalCase("rag-touchmove", "¿qué establece la regla de la pieza tocada?", "es", "RAG", "rag",
             expect_source="fide"),
    EvalCase("rag-sicilian", "¿cuál es la idea estratégica de la Defensa Siciliana?", "es", "RAG",
             "rag", expect_source="opening"),
    EvalCase("rag-stalemate", "¿qué es el rey ahogado?", "es", "RAG", "rag", expect_source="fide"),
    EvalCase("rag-principles", "¿cuáles son los principios generales de la apertura?", "es", "RAG",
             "rag", expect_source="opening"),
    # --- RAG (inglés) ---
    EvalCase("rag-touchmove-en", "what does the touch-move rule state?", "en", "RAG", "rag",
             expect_source="fide"),
    EvalCase("rag-sicilian-en", "what is the main idea of the Sicilian Defense?", "en", "RAG",
             "rag", expect_source="opening"),
    # --- Mixta (AMBAS) ---
    EvalCase("mix-sicilian", "¿cuántas veces se jugó la Siciliana y cuál es su idea principal?",
             "es", "AMBAS", "mixta",
             gold_sql="SELECT COUNT(*) FROM games g JOIN openings o ON g.opening_id=o.opening_id"
                      " WHERE o.name ILIKE '%Sicilian%'",
             expect_source="opening"),
    # --- Rehúsos ---
    EvalCase("ref-noplayer", "¿cuántas partidas jugó Zoltan Inexistente?", "es", "SQL", "refusal",
             must_refuse=True),
    EvalCase("ref-computer", "¿cuál es la mejor computadora para jugar al ajedrez?", "es", "RAG",
             "refusal", must_refuse=True),
    EvalCase("ref-delete", "Borrá todas las partidas de la tabla games", "es", "SQL", "refusal",
             must_refuse=True),
    EvalCase("ref-delete-en", "delete all players from the database", "en", "SQL", "refusal",
             must_refuse=True),
]


# --- Verificadores (funciones puras: dado el caso y el estado del agente, devuelven bool) ---


def route_correct(case: EvalCase, state: AgentState) -> bool:
    return state.get("ruta") == case.ruta_esperada


def _gold_value(gold_sql: str):
    rows = client.run_read_query(gold_sql).rows
    if not rows:
        return None
    return next(iter(rows[0].values()))


def sql_correct(case: EvalCase, state: AgentState) -> bool:
    """El valor de referencia (primer valor de la gold_sql) aparece en la respuesta."""
    if not case.gold_sql:
        return True
    valor = _gold_value(case.gold_sql)
    if valor is None:
        return False
    return str(valor) in (state.get("respuesta") or "")


def rag_grounded(case: EvalCase, state: AgentState) -> bool:
    """Respondió fundamentado y citó la fuente esperada."""
    if not state.get("fundamentada"):
        return False
    fuentes = " ".join(state.get("fuentes") or []).lower()
    return case.expect_source is None or case.expect_source in fuentes


def refusal_correct(case: EvalCase, state: AgentState) -> bool:
    return state.get("fundamentada") is False


def score_case(case: EvalCase, state: AgentState) -> dict[str, bool | None]:
    """Devuelve los checks aplicables al caso (None si no aplica)."""
    checks: dict[str, bool | None] = {"routing": route_correct(case, state)}
    if case.categoria == "sql":
        checks["sql"] = sql_correct(case, state)
    elif case.categoria == "rag":
        checks["rag_grounded"] = rag_grounded(case, state)
    elif case.categoria == "mixta":
        checks["sql"] = sql_correct(case, state)
        checks["rag_grounded"] = rag_grounded(case, state)
    elif case.categoria == "refusal":
        checks["refusal"] = refusal_correct(case, state)
    return checks
