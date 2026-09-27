"""Escenarios BDD de la ruta RAG (US2) — T019.

Cablea `docs/requirements/use-cases/rag-queries.feature` con pytest-bdd. Verifica recuperación,
cita de la fuente y rehúso cuando el tema no está en los documentos.

Requiere: PDFs indexados en `document_chunks` (correr `python -m chess_agent.rag.ingest`) +
Claude API (test de integración end-to-end).
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from chess_agent.db import client
from chess_agent.graph import run

scenarios("rag-queries.feature")


@pytest.fixture
def ctx() -> dict:
    return {}


@given("que el repositorio RAG contiene las Leyes FIDE y un texto de teoría de aperturas")
def _repo_listo():
    n = client.run_read_query("SELECT count(*) n FROM document_chunks").rows[0]["n"]
    assert n > 0, "no hay chunks indexados; correr chess_agent.rag.ingest"


@when(parsers.parse('el usuario pregunta "{pregunta}"'))
def _pregunta(ctx: dict, pregunta: str):
    ctx["state"] = run(pregunta)


@when("el agente responde una consulta por la ruta RAG")
def _consulta_rag(ctx: dict):
    ctx["state"] = run("¿qué establece la regla de la pieza tocada?")


@then("el agente recupera fragmentos de las Leyes FIDE")
@then("el agente recupera fragmentos del texto de teoría de aperturas")
def _recupera_fragmentos(ctx: dict):
    # Verifica que hubo recuperación efectiva por la ruta RAG.
    assert ctx["state"].get("chunks"), "no se recuperaron fragmentos"


@then("la respuesta explica la regla citando el documento fuente")
def _explica_con_cita(ctx: dict):
    assert ctx["state"].get("fundamentada") is True
    assert ctx["state"].get("fuentes")


@then("la respuesta describe la idea citando la fuente")
def _describe_con_cita(ctx: dict):
    assert ctx["state"].get("fundamentada") is True
    assert ctx["state"].get("fuentes")


@then("la respuesta incluye una referencia al documento del que se obtuvo la información")
def _incluye_referencia(ctx: dict):
    assert ctx["state"].get("fuentes"), "la respuesta no cita ninguna fuente"


@then("el agente responde que no encontró información en los documentos disponibles")
def _rehusa_docs(ctx: dict):
    respuesta = ctx["state"]["respuesta"].lower()
    assert ctx["state"].get("fundamentada") is False
    assert "document" in respuesta or "no encontr" in respuesta


@then("no inventa una respuesta")
def _no_inventa(ctx: dict):
    assert ctx["state"].get("fundamentada") is False
