"""Estado compartido del grafo LangGraph.

Es el objeto que fluye entre nodos (router → SQL/RAG → síntesis). Refleja el contrato de
consulta al agente (`specs/001-sql-rag-agent/contracts/agent-interface.md`): la entrada es
`pregunta` y la salida son `respuesta`, `ruta`, `sql_generado`, `fuentes` y `fundamentada`.
Los demás campos son evidencia intermedia que produce cada nodo.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

#son las opciones de donde buscar la info, si hacer la consulta, si usar el rag, o usar ambas.
Route = Literal["SQL", "RAG", "AMBAS"]


# Esta es la forma que tiene cada fragmento que devuelve el RAG cuando se busca en los PDFs.
# No solo se devuelve el texto, sino un objeto con 4 campos. Por ejemplo:
# {
#     "text": "La regla touch-move obliga al jugador a mover la pieza tocada...",
#     "source": "fide-laws-of-chess",
#     "page": 3,
#     "score": 0.71
# }
class RagChunk(TypedDict):
    """Fragmento recuperado por el RAG, con su procedencia (para citar)."""

    text: str
    source: str
    page: int
    score: float


#Esto es lo mas importante, es una clase que es como si fuera un sobre, definde todos los campos que va a haber durante
#el flujo, y se va pasando entre todas las clases y completando. Ahi esta dividido en orden por que parte se va
#completando primero y que parte del proyecto lo hace.
class AgentState(TypedDict, total=False):
    """Estado del agente. `total=False`: cada nodo completa solo sus campos."""

    # --- Entrada ---
    pregunta: str

    # --- Router ---
    ruta: Route
    idioma: Literal["es", "en"]

    # --- Evidencia del nodo SQL ---
    sql_generado: str | None
    sql_rows: list[dict[str, Any]]
    sql_error: str | None

    # --- Evidencia del nodo RAG ---
    chunks: list[RagChunk]
    fuentes: list[str]

    # --- Salida (síntesis) ---
    respuesta: str
    fundamentada: bool


# eca se instancia y se crea el primer campo que es la pregunta del usuario.
def initial_state(pregunta: str) -> AgentState:
    """Construye el estado inicial a partir de la pregunta del usuario."""
    return AgentState(pregunta=pregunta)
