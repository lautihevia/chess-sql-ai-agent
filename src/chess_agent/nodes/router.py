"""Nodo Router: clasifica la pregunta en una ruta (SQL / RAG / AMBAS) y detecta el idioma (T016).

Sigue `docs/agent/prompts/router.md`. En esta fase (MVP US1) las preguntas de datos deben
enrutarse a SQL; la ruta RAG/AMBAS ya queda soportada para las fases siguientes. Ante ambigüedad
o error del clasificador, cae por defecto a SQL (la ruta con datos verificables).
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import get_args

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from chess_agent.config import get_settings
from chess_agent.state import AgentState, Route

_VALID_ROUTES = set(get_args(Route))  # {"SQL", "RAG", "AMBAS"}

_SYSTEM = """\
Sos un clasificador de consultas de un asistente de ajedrez. Tu única tarea es decidir de
qué fuente debe obtenerse la respuesta. Respondé SOLO con una de estas etiquetas: SQL, RAG, AMBAS.

Criterios:
- SQL  -> datos concretos de una base relacional: jugadores, ratings, partidas, resultados,
         torneos, aperturas (como dato/conteo). Ej.: "¿cuántas partidas ganó X?", "top 5 por rating".
- RAG  -> conocimiento textual: reglas del ajedrez, definiciones, ideas estratégicas.
         Ej.: "¿qué dice la regla FIDE sobre...?", "¿cuál es la idea de la Siciliana?".
- AMBAS -> mezcla un dato relacional Y un concepto textual en una sola frase.

No respondas la pregunta. No expliques. Devolvé solo la etiqueta."""

# Señales de español (caracteres y palabras/raíces frecuentes) para detección de idioma ligera.
# Se usan raíces (jug, partid, apertur…) para cubrir plurales y conjugaciones, y stopwords
# que no aparecen en inglés (la, los, por, del…).
_ES_CHARS = re.compile(r"[¿¡áéíóúñ]", re.IGNORECASE)
_ES_WORDS = re.compile(
    r"\b(el|la|los|las|un|una|unos|unas|de|del|por|con|para|qué|cuál|cuáles|cuántas|cuántos|"
    r"cómo|quién|dónde|cuándo|jug\w*|partid\w*|torneo\w*|apertur\w*|gan\w*|país|países|"
    r"promedio|tablas|mayor|menor|ajedrez)\b",
    re.IGNORECASE,
)


@lru_cache(maxsize=1)
def _llm() -> ChatAnthropic:
    settings = get_settings()
    return ChatAnthropic(
        model=settings.anthropic_model,
        api_key=settings.anthropic_api_key,
        temperature=0,
        max_tokens=8,
    )


def _detect_language(pregunta: str) -> str:
    if _ES_CHARS.search(pregunta) or _ES_WORDS.search(pregunta):
        return "es"
    return "en"


#le pregutna a claude para que clasifique si es por SQL o RAG.
def _classify(pregunta: str) -> Route:
    try:
        respuesta = _llm().invoke(
            [SystemMessage(content=_SYSTEM), HumanMessage(content=pregunta)]
        )
        etiqueta = str(respuesta.content).strip().upper()
    except Exception:
        return "SQL"
    for ruta in _VALID_ROUTES:
        if ruta in etiqueta:
            return ruta  # type: ignore[return-value]
    return "SQL"


def router(state: AgentState) -> AgentState:
    pregunta = state["pregunta"]
    return {"ruta": _classify(pregunta), "idioma": _detect_language(pregunta)}
