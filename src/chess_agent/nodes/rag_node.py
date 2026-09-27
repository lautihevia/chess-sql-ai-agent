"""Nodo RAG: recupera fragmentos de los PDFs indexados para la pregunta (T024).

Sigue `docs/agent/prompts/rag.md`. Deja los fragmentos y sus fuentes en el estado. La decisión
de si el contexto realmente responde la pregunta la toma el nodo de síntesis (que rehúsa con
NO_ANSWER si el material recuperado no cubre la consulta), por lo que acá se recupera con recall
alto (umbral bajo del recuperador).
"""

from __future__ import annotations

from chess_agent.rag.retriever import retrieve
from chess_agent.state import AgentState


def rag_node(state: AgentState) -> AgentState:
    chunks = retrieve(state["pregunta"])
    fuentes = sorted({f"{c['source']} (p. {c['page']})" for c in chunks})
    return {"chunks": chunks, "fuentes": fuentes}
