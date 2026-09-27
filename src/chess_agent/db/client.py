"""Cliente de acceso a la BD de Supabase (Postgres).

El agente consulta la BD en **solo lectura** (Principio II de la constitución). Esta capa fuerza
ese modo a nivel de conexión (`read_only = True`) como defensa en profundidad, además de los
guardrails del validador SQL. También acota cada consulta con un `statement_timeout`.

Las operaciones de escritura (aplicar el esquema, cargar el seed) usan `connect(read_only=False)`
explícitamente y solo se invocan desde scripts de setup, nunca desde el agente.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import psycopg
from psycopg.rows import dict_row

from chess_agent.config import get_settings

# Tope de tiempo por consulta (ms). Evita que una query costosa cuelgue la app.
STATEMENT_TIMEOUT_MS = 10_000


#Ese frozen = true, significa que el objeto es inmutable, por eso se agrega
@dataclass(frozen=True)
class QueryResult:
    """Resultado de una consulta de lectura."""

    columns: list[str]          # nombres de las columnas devueltas por la query
    rows: list[dict[str, Any]]  # filas como diccionarios {columna: valor}

    # @property permite acceder a row_count como si fuera un campo (result.row_count),
    # pero en realidad es una función que calcula el valor en el momento, no se guarda en el objeto.
    @property
    def row_count(self) -> int:
        return len(self.rows)


def _conninfo() -> str:
    """URL de conexión, asegurando SSL (Supabase lo requiere)."""
    url = get_settings().supabase_db_url
    if "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url


#Es un decorador que convierte una función en algo que se puede usar con with.
#Su utilidad principal es garantizar que el código de limpieza siempre se ejecute.
@contextmanager
def connect(*, read_only: bool = True) -> Iterator[psycopg.Connection]:
    """Abre una conexión a la BD.

    Por defecto es de **solo lectura**. `read_only=False` solo para setup (schema/seed).
    """
    with psycopg.connect(_conninfo(), row_factory=dict_row) as conn:
        # read_only=True le dice a PostgreSQL que rechace cualquier escritura a nivel de BD.
        # Es la segunda capa de seguridad (la primera es el validador SQL en sql/validator.py).
        # Debe fijarse antes de iniciar cualquier transacción.
        conn.read_only = read_only
        yield conn  # pausa acá y entrega la conexión al bloque "with"; al salir, cierra la conexión


def run_read_query(sql: str, params: Sequence[Any] | None = None) -> QueryResult:
    """Ejecuta una consulta de **solo lectura** y devuelve columnas + filas.

    La conexión está en modo read-only: cualquier intento de escritura que se cuele hasta acá
    es rechazado por el propio Postgres. Además se aplica un `statement_timeout` acotado.
    """
    # Se abren dos contextos a la vez: la conexión y el cursor (puntero para ejecutar queries).
    with connect(read_only=True) as conn, conn.cursor() as cur:
        # Limita el tiempo máximo de ejecución. Si la query tarda más de 10s, Postgres la cancela.
        cur.execute(f"SET statement_timeout = {STATEMENT_TIMEOUT_MS}")
        cur.execute(sql, params)
        rows = cur.fetchall()  # trae todas las filas del resultado
        # cur.description tiene metadata de las columnas; se extrae solo el nombre de cada una.
        columns = [desc.name for desc in cur.description] if cur.description else []
        return QueryResult(columns=columns, rows=list(rows))


def ping() -> bool:
    """Verifica conectividad con la BD (usado en pruebas de conexión end-to-end)."""
    result = run_read_query("SELECT 1 AS ok")
    return result.rows == [{"ok": 1}]
