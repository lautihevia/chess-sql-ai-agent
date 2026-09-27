"""Nodo SQL: genera SQL desde la pregunta, lo valida, lo ejecuta (solo lectura) y reintenta
una vez con el mensaje de error si la ejecución falla (T015).

Nunca ejecuta escrituras: el validador rechaza todo lo que no sea un SELECT y la conexión es
de solo lectura. Deja la evidencia en el estado (`sql_generado`, `sql_rows`, `sql_error`) para
que el nodo de síntesis redacte con grounding.
"""

from __future__ import annotations

from chess_agent.db.client import run_read_query
from chess_agent.sql.generator import NO_SQL, generate_sql
from chess_agent.sql.validator import SqlValidationError, validate_sql
from chess_agent.state import AgentState


def _try_execute(raw: str) -> tuple[str, list[dict] | None, str | None]:
    """Valida y ejecuta un SQL crudo. Devuelve (sql_usado, filas|None, error|None)."""
    try:
        sql = validate_sql(raw)
    except SqlValidationError as exc:
        return raw, None, f"SQL rechazado por seguridad: {exc}"
    try:
        result = run_read_query(sql)
        return sql, result.rows, None
    except Exception as exc:  # errores de PostgreSQL (columna inexistente, sintaxis, etc.)
        return sql, None, str(exc)


def sql_node(state: AgentState) -> AgentState:
    pregunta = state["pregunta"]

    raw = generate_sql(pregunta)
    if raw.strip() == NO_SQL:
        return {"sql_generado": None, "sql_rows": [], "sql_error": NO_SQL}

    sql, rows, error = _try_execute(raw)
    if error is None:
        return {"sql_generado": sql, "sql_rows": rows, "sql_error": None}

    # Un único reintento, pasándole el error al generador para que corrija.
    raw2 = generate_sql(pregunta, error_previo=error)
    if raw2.strip() == NO_SQL:
        return {"sql_generado": sql, "sql_rows": [], "sql_error": error}

    sql2, rows2, error2 = _try_execute(raw2)
    if error2 is None:
        return {"sql_generado": sql2, "sql_rows": rows2, "sql_error": None}
    return {"sql_generado": sql2, "sql_rows": [], "sql_error": error2}
