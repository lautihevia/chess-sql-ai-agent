"""Nodo Síntesis: redacta la respuesta final SOLO con la evidencia reunida (T017).

Aplica `docs/agent/grounding-policy.md`:
- si hay evidencia (filas SQL reales o fragmentos RAG), redacta con Claude usando solo eso;
- si no la hay, rehúsa honestamente (`fundamentada = False`) y no inventa;
- ante un pedido de escritura, aclara que solo puede consultar (lectura);
- siempre responde en el idioma de la pregunta.

El flag `fundamentada` se decide de forma programática (no lo delega al LLM) para que el
grounding sea verificable.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from chess_agent.config import get_settings
from chess_agent.state import AgentState

# Intención de escritura en la pregunta (para el rehúso de seguridad explícito).
_WRITE_INTENT = re.compile(
    r"\b(borr\w*|elimin\w*|actualiz\w*|insert\w*|modific\w*|drop|delete|update|truncate|"
    r"remove|wipe|altera\w*|vaciar?)\b",
    re.IGNORECASE,
)

_REFUSAL = {
    "solo_lectura": {
        "es": "Solo puedo realizar consultas de lectura sobre la base de datos; "
        "no puedo modificar, borrar ni insertar datos.",
        "en": "I can only run read-only queries on the database; "
        "I can't modify, delete or insert data.",
    },
    "sin_datos": {
        "es": "No encontré información para responder esa consulta en los datos disponibles.",
        "en": "I couldn't find information to answer that query in the available data.",
    },
    "sin_docs": {
        "es": "No encontré esa información en los documentos disponibles.",
        "en": "I couldn't find that information in the available documents.",
    },
}

_NO_ANSWER = "NO_ANSWER"

_SYSTEM = """\
Sos un asistente de ajedrez. Redactá una respuesta clara y concisa usando SOLO la evidencia
provista. Reglas:
- Si hay RESULTADO_SQL, basá los datos numéricos/fácticos en él, sin alterarlo ni inventar.
- Si hay CONTEXTO_RAG, usalo para la parte conceptual y citá la fuente.
- No inventes datos, cifras ni fuentes.
- Si la evidencia provista NO contiene información suficiente para responder la pregunta,
  respondé EXACTAMENTE con la palabra: {no_answer} (sin ningún otro texto).
- Respondé SIEMPRE en este idioma: {idioma}."""


@lru_cache(maxsize=1)
def _llm() -> ChatAnthropic:
    settings = get_settings()
    return ChatAnthropic(
        model=settings.anthropic_model,
        api_key=settings.anthropic_api_key,
        temperature=0,
        max_tokens=500,
    )


def _has_sql_evidence(rows: list[dict[str, Any]]) -> bool:
    """Hay evidencia SQL salvo que sea un único agregado nulo/cero (entidad sin datos)."""
    if not rows:
        return False
    if len(rows) == 1 and len(rows[0]) == 1:
        value = next(iter(rows[0].values()))
        if value in (0, None):
            return False
    return True


def _refuse(state: AgentState, idioma: str) -> str:
    sql_error = (state.get("sql_error") or "").lower()
    pregunta = state.get("pregunta", "")
    if "seguridad" in sql_error or "rechazado" in sql_error or _WRITE_INTENT.search(pregunta):
        return _REFUSAL["solo_lectura"][idioma]
    # Preguntas conceptuales (RAG/AMBAS) sin fragmentos: rehúso referido a los documentos.
    if state.get("ruta") in ("RAG", "AMBAS"):
        return _REFUSAL["sin_docs"][idioma]
    return _REFUSAL["sin_datos"][idioma]


def _draft(state: AgentState, idioma: str) -> str:
    partes = [f"PREGUNTA:\n{state.get('pregunta', '')}"]
    rows = state.get("sql_rows") or []
    if rows:
        partes.append(
            "RESULTADO_SQL:\n" + json.dumps(rows, default=str, ensure_ascii=False)
        )
    chunks = state.get("chunks") or []
    if chunks:
        contexto = "\n---\n".join(
            f"[{c['source']} p.{c['page']}] {c['text']}" for c in chunks
        )
        partes.append("CONTEXTO_RAG:\n" + contexto)

    respuesta = _llm().invoke(
        [
            SystemMessage(content=_SYSTEM.format(idioma=idioma, no_answer=_NO_ANSWER)),
            HumanMessage(content="\n\n".join(partes)),
        ]
    )
    return str(respuesta.content).strip()


def synthesis(state: AgentState) -> AgentState:
    idioma = state.get("idioma", "es")
    sql_ok = state.get("sql_error") is None and _has_sql_evidence(state.get("sql_rows") or [])
    rag_ok = bool(state.get("chunks"))
    fuentes = state.get("fuentes") or []

    if not (sql_ok or rag_ok):
        return {"respuesta": _refuse(state, idioma), "fundamentada": False, "fuentes": fuentes}

    draft = _draft(state, idioma)
    # El LLM señala con NO_ANSWER que la evidencia recuperada no cubre la pregunta: se convierte
    # en un rehúso honesto (evita respuestas "fundamentadas" que en realidad no responden).
    if draft.strip().upper().startswith(_NO_ANSWER):
        return {"respuesta": _refuse(state, idioma), "fundamentada": False, "fuentes": []}

    return {"respuesta": draft, "fundamentada": True, "fuentes": fuentes}
