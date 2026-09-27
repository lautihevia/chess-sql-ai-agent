"""Interfaz Streamlit del agente de ajedrez (T018).

Chat conversacional que muestra, en vivo, el proceso de razonamiento del agente
(router → SQL/RAG → síntesis), los resultados SQL como tabla, badges con la ruta/idioma/latencia
y el historial de la conversación. Ejecutar con:

    uv run streamlit run src/app.py
"""

from __future__ import annotations

import time
from typing import Any

import pandas as pd
import streamlit as st

from chess_agent.graph import build_graph
from chess_agent.state import initial_state

EJEMPLOS = [
    "¿Cuántas partidas ganó Carlsen con blancas?",
    "¿Cuáles son los 5 jugadores con mayor peak rating?",
    "¿Qué establece la regla de la pieza tocada?",
    "¿Cuántas veces se jugó la Siciliana y cuál es su idea principal?",
]

# Etiqueta "humana" que se muestra en el panel de progreso mientras corre cada nodo del grafo.
_PASOS = {
    "router": "🧭 Analizando la pregunta y eligiendo la fuente…",
    "sql_node": "🗄️ Generando y ejecutando la consulta SQL…",
    "rag_node": "📚 Buscando en los documentos (RAG)…",
    "synthesis": "✍️ Redactando la respuesta con fundamento…",
}

# Color del badge según la ruta elegida por el router.
_COLOR_RUTA = {"SQL": "blue", "RAG": "green", "AMBAS": "violet"}

st.set_page_config(page_title="Chess SQL AI Agent", page_icon="♟️", layout="centered")


@st.cache_resource
def _graph():
    """Compila el grafo una sola vez por sesión del servidor."""
    return build_graph()


def _stream_respuesta(pregunta: str) -> dict[str, Any]:
    """Ejecuta el grafo en streaming y va mostrando cada paso en vivo.

    `graph.stream(..., stream_mode="updates")` emite, por cada nodo que termina, un dict
    `{nombre_nodo: cambios_en_el_estado}`. Vamos acumulando esos cambios para reconstruir el
    estado final y, de paso, actualizamos el panel de progreso con el nodo en curso.
    """
    estado: dict[str, Any] = {}
    with st.status("Pensando…", expanded=True) as status:
        for update in _graph().stream(initial_state(pregunta), stream_mode="updates"):
            for nodo, delta in update.items():
                st.write(_PASOS.get(nodo, f"Ejecutando {nodo}…"))
                if delta:
                    estado.update(delta)  # mergea la evidencia que produjo este nodo
        status.update(label="Listo", state="complete", expanded=False)
    return estado


def _badges(estado: dict[str, Any], segundos: float) -> None:
    """Muestra chips de color con la ruta, el idioma y la latencia."""
    ruta = estado.get("ruta", "—")
    color = _COLOR_RUTA.get(ruta, "gray")
    idioma = "🇦🇷 Español" if estado.get("idioma") == "es" else "🇬🇧 English"
    st.markdown(
        f":{color}-badge[Ruta: {ruta}] &nbsp; :gray-badge[{idioma}] "
        f"&nbsp; :orange-badge[⏱️ {segundos:.1f}s]"
    )


def _render_respuesta(estado: dict[str, Any], segundos: float) -> None:
    """Dibuja una respuesta completa: badges + texto + tabla SQL + detalles."""
    _badges(estado, segundos)

    if estado.get("fundamentada"):
        st.markdown(estado["respuesta"])
    else:
        st.warning(estado.get("respuesta", "No pude responder con la información disponible."))

    # Resultados crudos de la consulta como tabla (solo si el nodo SQL devolvió filas).
    filas = estado.get("sql_rows")
    if filas:
        st.markdown("**Resultados de la consulta:**")
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

    if estado.get("fuentes"):
        st.caption("📚 Fuentes: " + " · ".join(estado["fuentes"]))

    with st.expander("Detalles de la ejecución"):
        if estado.get("sql_generado"):
            st.markdown("**SQL generado:**")
            st.code(estado["sql_generado"], language="sql")
        if estado.get("fuentes"):
            st.markdown("**Fuentes citadas:**")
            for f in estado["fuentes"]:
                st.markdown(f"- {f}")
        if not estado.get("sql_generado") and not estado.get("fuentes"):
            st.caption("Sin evidencia estructurada para esta respuesta.")


# --- Cabecera ---
st.title("♟️ Chess SQL AI Agent")
st.caption(
    "Preguntá en lenguaje natural (español o inglés) sobre partidas, jugadores y torneos. "
    "El agente decide la fuente, genera SQL de solo lectura y responde con fundamento."
)

# --- Panel lateral con ejemplos ---
with st.sidebar:
    st.subheader("Ejemplos")
    st.caption("Hacé clic para preguntar directamente:")
    for ej in EJEMPLOS:
        if st.button(ej, use_container_width=True):
            st.session_state["pendiente"] = ej  # se procesa al re-ejecutar el script
    st.divider()
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state["historial"] = []
        st.rerun()

# --- Historial de conversación (estilo chat) ---
# Cada turno se guarda como {"pregunta", "estado", "segundos"} y se vuelve a dibujar en cada run.
if "historial" not in st.session_state:
    st.session_state["historial"] = []

for turno in st.session_state["historial"]:
    with st.chat_message("user"):
        st.markdown(turno["pregunta"])
    with st.chat_message("assistant"):
        _render_respuesta(turno["estado"], turno["segundos"])

# --- Entrada del usuario ---
# La pregunta puede venir del input de chat o de un botón de ejemplo (session_state["pendiente"]).
pregunta = st.chat_input("Escribí tu pregunta sobre ajedrez…")
if not pregunta:
    pregunta = st.session_state.pop("pendiente", None)

if pregunta and pregunta.strip():
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        inicio = time.perf_counter()
        estado = _stream_respuesta(pregunta)
        segundos = time.perf_counter() - inicio
        _render_respuesta(estado, segundos)

    st.session_state["historial"].append(
        {"pregunta": pregunta, "estado": estado, "segundos": segundos}
    )
