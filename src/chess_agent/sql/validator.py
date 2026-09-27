"""Validador de SQL: guardrails de solo lectura (Contrato 2, Principio II).

Antes de ejecutar cualquier SQL generado por el LLM se valida acá:
- debe ser UNA sola sentencia `SELECT` (o `WITH ... SELECT`);
- se rechaza cualquier escritura o DDL (INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/…);
- se rechazan múltiples sentencias;
- si no trae `LIMIT`, se le agrega uno de seguridad.

Es la primera línea de defensa; la segunda es la conexión de solo lectura (`db/client.py`).
"""

from __future__ import annotations

import re

DEFAULT_MAX_LIMIT = 100

# Palabras clave prohibidas (escritura, DDL, control). Se buscan como token completo.
_FORBIDDEN = (
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "REPLACE",
    "GRANT", "REVOKE", "MERGE", "CALL", "EXECUTE", "EXEC", "VACUUM", "COMMENT",
    "COPY", "INTO", "SET", "REINDEX", "REFRESH",
)

_STARTS_OK = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
_HAS_LIMIT = re.compile(r"\bLIMIT\b", re.IGNORECASE)


class SqlValidationError(ValueError):
    """El SQL propuesto no es una consulta de solo lectura válida."""


def _strip_fences(sql: str) -> str:
    """Quita cercos de markdown (```sql ... ```) por si el LLM los incluye."""
    s = sql.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s)
    return s.strip()


def validate_sql(sql: str, max_limit: int = DEFAULT_MAX_LIMIT) -> str:
    """Valida y sanea el SQL. Devuelve la consulta lista para ejecutar.

    Lanza `SqlValidationError` si no es un único SELECT de solo lectura.
    """
    if not sql or not sql.strip():
        raise SqlValidationError("SQL vacío.")

    cleaned = _strip_fences(sql).rstrip()

    # Quitar un único punto y coma final; cualquier otro `;` implica múltiples sentencias.
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].rstrip()
    if ";" in cleaned:
        raise SqlValidationError("No se permiten múltiples sentencias.")

    if not _STARTS_OK.match(cleaned):
        raise SqlValidationError("Solo se permiten consultas SELECT (o WITH ... SELECT).")

    upper = cleaned.upper()
    for kw in _FORBIDDEN:
        if re.search(rf"\b{kw}\b", upper):
            raise SqlValidationError(f"Operación no permitida en modo solo lectura: {kw}.")

    if not _HAS_LIMIT.search(cleaned):
        cleaned = f"{cleaned} LIMIT {max_limit}"

    return cleaned
