"""Escenarios BDD de enrutamiento (US3) — T027.

Cablea `docs/requirements/use-cases/routing.feature`: verifica que el router elige la fuente
correcta (SQL / RAG / AMBAS), que la rama AMBAS combina ambos insumos y que el idioma se respeta.

Requiere: BD seedeada + PDFs indexados + Claude API.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from chess_agent.db import client
from chess_agent.graph import run

scenarios("routing.feature")


@pytest.fixture
def ctx() -> dict:
    return {}


@given("que la base de datos contiene partidas, jugadores, aperturas y torneos")
def _db_lista():
    assert client.ping()


@given("que el repositorio RAG contiene las Leyes FIDE y un texto de teoría de aperturas")
def _repo_listo():
    n = client.run_read_query("SELECT count(*) n FROM document_chunks").rows[0]["n"]
    assert n > 0


@when(parsers.parse('el usuario pregunta "{pregunta}"'))
def _pregunta(ctx: dict, pregunta: str):
    ctx["state"] = run(pregunta)


@then(parsers.parse("el agente enruta la consulta a {ruta}"))
def _enruta(ctx: dict, ruta: str):
    assert ctx["state"].get("ruta") == ruta


@then("no consulta el repositorio RAG")
def _sin_rag(ctx: dict):
    assert not ctx["state"].get("chunks")


@then("no genera una consulta SQL")
def _sin_sql(ctx: dict):
    assert ctx["state"].get("sql_generado") is None


@then("combina el resultado de SQL con el contexto de RAG en la respuesta")
def _combina(ctx: dict):
    estado = ctx["state"]
    assert estado.get("sql_generado"), "no generó SQL en la ruta AMBAS"
    assert estado.get("chunks"), "no recuperó contexto RAG en la ruta AMBAS"
    assert estado.get("fundamentada") is True


@then("responde en inglés")
def _en_ingles(ctx: dict):
    assert ctx["state"].get("idioma") == "en"
