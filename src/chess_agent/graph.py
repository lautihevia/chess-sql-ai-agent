"""Definición del grafo LangGraph: router → (SQL / RAG / AMBAS) → síntesis.

Este módulo cablea los nodos y expone `build_graph()` / `run(pregunta)`. En esta fase los nodos
son stubs; su lógica se completa en las Fases 3-5. El cableado ya soporta las tres rutas:

    router ─┬─ SQL   → sql_node ───────────────→ synthesis → END
            ├─ RAG   → rag_node ───────────────→ synthesis → END
            └─ AMBAS → sql_node → rag_node ────→ synthesis → END

La rama AMBAS se resuelve de forma secuencial (SQL y luego RAG) para evitar escrituras
concurrentes sobre el estado; la Fase 5 (T029) puede refinarla.
"""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

from chess_agent.config import configure_langsmith
from chess_agent.nodes.rag_node import rag_node
from chess_agent.nodes.router import router
from chess_agent.nodes.sql_node import sql_node
from chess_agent.nodes.synthesis import synthesis
from chess_agent.state import AgentState, initial_state


def _select_after_router(state: AgentState) -> Literal["sql_node", "rag_node"]:
    """SQL y AMBAS empiezan por el nodo SQL; RAG va directo al nodo RAG."""
    return "rag_node" if state.get("ruta") == "RAG" else "sql_node"


def _select_after_sql(state: AgentState) -> Literal["rag_node", "synthesis"]:
    """En la ruta AMBAS, tras SQL se ejecuta RAG; en SQL puro se pasa a síntesis."""
    return "rag_node" if state.get("ruta") == "AMBAS" else "synthesis"


def build_graph():
    """Construye y compila el grafo del agente."""
    configure_langsmith()  # activa el trazado si hay credenciales (Principio IV)
    builder = StateGraph(AgentState)

    builder.add_node("router", router)
    builder.add_node("sql_node", sql_node)
    builder.add_node("rag_node", rag_node)
    builder.add_node("synthesis", synthesis)

    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router",
        _select_after_router,
        {"sql_node": "sql_node", "rag_node": "rag_node"},
    )
    builder.add_conditional_edges(
        "sql_node",
        _select_after_sql,
        {"rag_node": "rag_node", "synthesis": "synthesis"},
    )
    builder.add_edge("rag_node", "synthesis")
    builder.add_edge("synthesis", END)

    return builder.compile()


def run(pregunta: str) -> AgentState:
    """Ejecuta el grafo completo para una pregunta y devuelve el estado final."""
    graph = build_graph()
    return graph.invoke(initial_state(pregunta))
