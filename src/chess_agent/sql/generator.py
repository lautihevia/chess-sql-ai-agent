"""Generador text-to-SQL: convierte la pregunta en una consulta PostgreSQL de solo lectura.

Sigue `docs/agent/prompts/sql.md`. El prompt inyecta tres piezas:
- el esquema real (`db/schema.sql`), fuente de verdad de tablas y columnas;
- ejemplos few-shot curados (de `docs/agent/golden-queries.md`);
- el mapeo de términos lenguaje↔esquema (de `docs/data/term-mapping.md`).

Si la pregunta no se puede responder con el esquema, el modelo devuelve el sentinel `NO_SQL`.
La salida NO se ejecuta directamente: pasa antes por `validator.validate_sql`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from chess_agent.config import get_settings

NO_SQL = "NO_SQL"

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "db" / "schema.sql"

# Ejemplos few-shot (subconjunto de docs/agent/golden-queries.md).
_FEW_SHOT = """\
P: ¿Cuántas partidas ganó Magnus Carlsen con blancas?
SQL: SELECT COUNT(*) FROM games g JOIN players p ON g.white_player_id=p.player_id WHERE p.name ILIKE '%Carlsen%' AND g.result='1-0';

P: ¿Cuántas partidas ganó Carlsen en total?
SQL: SELECT COUNT(*) FROM games g JOIN players p ON p.player_id IN (g.white_player_id,g.black_player_id) WHERE p.name ILIKE '%Carlsen%' AND ((g.white_player_id=p.player_id AND g.result='1-0') OR (g.black_player_id=p.player_id AND g.result='0-1'));

P: Top 5 jugadores por peak rating
SQL: SELECT name, peak_rating FROM players ORDER BY peak_rating DESC NULLS LAST LIMIT 5;

P: ¿Cuál fue la apertura más jugada en el Tata Steel 2023?
SQL: SELECT o.name, COUNT(*) c FROM games g JOIN openings o ON g.opening_id=o.opening_id JOIN tournaments t ON g.tournament_id=t.tournament_id WHERE t.name ILIKE '%Tata Steel%' GROUP BY o.name ORDER BY c DESC LIMIT 1;

P: Rating promedio de los jugadores de Noruega
SQL: SELECT AVG(peak_rating) FROM players WHERE country='Norway';

P: ¿Cuántas partidas terminaron en tablas?
SQL: SELECT COUNT(*) FROM games WHERE result='1/2-1/2';

P: ¿Cuántas veces se jugó la Defensa Siciliana?
SQL: SELECT COUNT(*) FROM games g JOIN openings o ON g.opening_id=o.opening_id WHERE o.name ILIKE '%Sicilian%';
"""

# Reglas de mapeo (resumen de docs/data/term-mapping.md).
_TERM_MAPPING = """\
- "ganó con blancas" -> white_player_id = <jugador> AND result = '1-0'
- "ganó con negras" -> black_player_id = <jugador> AND result = '0-1'
- "ganó" (total) -> victorias con blancas ('1-0') o negras ('0-1') segun el color en cada partida
- "empató"/"tablas"/"draw" -> result = '1/2-1/2'
- "rating"/"ELO" -> players.peak_rating (maximo) o player_ratings.rating (evolucion)
- "título"/"GM"/"Gran Maestro" -> players.title
- "país"/"de Noruega" -> players.country / tournaments.country
- "apertura"/"Siciliana" -> openings.name (usar ILIKE '%...%')
- "torneo" -> tournaments.name (usar ILIKE '%...%')
- nombres de jugador/apertura/torneo: comparar con ILIKE '%texto%'
- "más"/"top N"/"el mayor" -> ORDER BY ... DESC LIMIT N; "promedio" -> AVG(...); "cuántos" -> COUNT(*)
"""

_SYSTEM_TEMPLATE = """\
Sos un generador de SQL para PostgreSQL. Convertí la pregunta del usuario en UNA consulta
SELECT válida y de solo lectura sobre el siguiente esquema. Reglas estrictas:

- Usá EXCLUSIVAMENTE las tablas y columnas del esquema provisto. No inventes nombres.
- Respetá los valores válidos (ej. result solo puede ser '1-0', '0-1', '1/2-1/2').
- Prohibido INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE o cualquier escritura.
- Devolvé SOLO el SQL, sin explicación ni markdown.
- Si la pregunta NO se puede responder con este esquema, devolvé exactamente: {no_sql}

ESQUEMA:
{schema}

EJEMPLOS (few-shot):
{few_shot}

MAPEO DE TÉRMINOS (lenguaje natural -> esquema):
{term_mapping}
"""


@lru_cache(maxsize=1)
def _load_schema() -> str:
    return _SCHEMA_PATH.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _llm() -> ChatAnthropic:
    settings = get_settings()
    return ChatAnthropic(
        model=settings.anthropic_model,
        api_key=settings.anthropic_api_key,
        temperature=0,
        max_tokens=512,
    )


@lru_cache(maxsize=1)
def _system_prompt() -> str:
    return _SYSTEM_TEMPLATE.format(
        no_sql=NO_SQL,
        schema=_load_schema(),
        few_shot=_FEW_SHOT,
        term_mapping=_TERM_MAPPING,
    )


def generate_sql(pregunta: str, error_previo: str | None = None) -> str:
    """Genera SQL para `pregunta`. Devuelve el SQL crudo o `NO_SQL`.

    Si `error_previo` viene dado (reintento), se incluye para que el modelo corrija el SQL.
    """
    human = f"Pregunta: {pregunta}"
    if error_previo:
        human += (
            f"\n\nEl intento anterior falló con este error de PostgreSQL:\n{error_previo}\n"
            "Devolvé una consulta corregida (solo el SQL)."
        )

    # .invoke() es el método de LangChain para llamar al modelo. Recibe una lista de mensajes:
    # - SystemMessage: las instrucciones fijas (esquema, reglas, ejemplos). Claude las lee primero.
    # - HumanMessage: la pregunta del usuario (puede incluir el error si es un reintento).
    #
    # Por qué usamos LangChain (ChatAnthropic) en vez del SDK de Anthropic directo:
    # LangSmith se engancha automáticamente a cada .invoke() y registra la traza completa
    # (prompt enviado, respuesta recibida, latencia, tokens) sin que tengamos que instrumentar nada.
    # Eso nos permite ver en langsmith.com qué SQL generó el modelo para cada pregunta,
    # detectar errores y medir el rendimiento del agente en producción.
    respuesta = _llm().invoke(
        [SystemMessage(content=_system_prompt()), HumanMessage(content=human)]
    )
    return str(respuesta.content).strip()
