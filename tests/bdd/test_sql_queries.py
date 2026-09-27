"""Escenarios BDD de la ruta SQL (US1) — T011.

Cablea `docs/requirements/use-cases/sql-queries.feature` con pytest-bdd. Escrito antes de la
implementación de los nodos (test-first). Los valores esperados se calculan contra la BD real
(no se hardcodean), por lo que las aserciones siguen siendo válidas si cambia el seed.

Requiere: BD seedeada + Claude API (test de integración end-to-end del agente).
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from chess_agent.db import client
from chess_agent.graph import run

scenarios("sql-queries.feature")


@pytest.fixture
def ctx() -> dict:
    return {}


# --- Antecedentes / Dado ---


@given("que la base de datos contiene datos sintéticos de partidas de ajedrez")
def _db_lista():
    assert client.ping()


@given(parsers.parse('que existen partidas de "{jugador}"'))
def _existe_jugador(jugador: str):
    r = client.run_read_query(
        "SELECT count(*) n FROM players WHERE name ILIKE %s", (f"%{jugador.split()[-1]}%",)
    )
    assert r.rows[0]["n"] >= 1


# --- Cuando ---


@when(parsers.parse('el usuario pregunta "{pregunta}"'))
def _pregunta(ctx: dict, pregunta: str):
    ctx["state"] = run(pregunta)


@when(parsers.parse('el usuario pide "{pregunta}"'))
def _pide(ctx: dict, pregunta: str):
    ctx["state"] = run(pregunta)


# --- Entonces ---


@then("el agente genera una consulta SQL de solo lectura")
def _genera_sql_lectura(ctx: dict):
    sql = ctx["state"].get("sql_generado")
    assert sql, "no se generó SQL"
    assert sql.strip().upper().startswith(("SELECT", "WITH"))


@then(parsers.parse("la respuesta contiene el conteo correcto de partidas con result '{result}'"))
def _conteo_correcto(ctx: dict, result: str):
    esperado = client.run_read_query(
        "SELECT count(*) n FROM games g JOIN players p ON g.white_player_id = p.player_id"
        " WHERE p.name ILIKE %s AND g.result = %s",
        ("%Carlsen%", result),
    ).rows[0]["n"]
    assert str(esperado) in ctx["state"]["respuesta"]


@then(parsers.parse("la respuesta lista {n:d} jugadores ordenados de mayor a menor peak_rating"))
def _ranking(ctx: dict, n: int):
    top = client.run_read_query(
        "SELECT name FROM players ORDER BY peak_rating DESC NULLS LAST LIMIT %s", (n,)
    ).rows
    respuesta = ctx["state"]["respuesta"]
    encontrados = sum(1 for row in top if row["name"] in respuesta)
    assert encontrados >= n - 1, f"solo {encontrados}/{n} jugadores del top en la respuesta"


@then("el agente une las tablas games, openings y tournaments")
def _hace_joins(ctx: dict):
    sql = (ctx["state"].get("sql_generado") or "").lower()
    assert "games" in sql and "openings" in sql and "tournaments" in sql


@then("devuelve el nombre de la apertura con más partidas en ese torneo")
def _apertura_top(ctx: dict):
    top = client.run_read_query(
        "SELECT o.name FROM games g"
        " JOIN openings o ON g.opening_id = o.opening_id"
        " JOIN tournaments t ON g.tournament_id = t.tournament_id"
        " WHERE t.name ILIKE %s GROUP BY o.name ORDER BY count(*) DESC LIMIT 1",
        ("%Tata Steel%",),
    ).rows
    assert top, "sin datos para el torneo"
    assert top[0]["name"] in ctx["state"]["respuesta"]


@then("la respuesta contiene un promedio calculado sobre los jugadores de ese país")
def _promedio_pais(ctx: dict):
    avg = client.run_read_query(
        "SELECT round(avg(peak_rating)) a FROM players WHERE country = 'Norway'"
    ).rows[0]["a"]
    assert avg is not None
    # Tolerante al formato: los tres primeros dígitos del promedio deben aparecer.
    assert str(int(avg))[:3] in ctx["state"]["respuesta"]


@then("el agente responde que no encontró información para ese jugador")
def _rehusa_jugador(ctx: dict):
    respuesta = ctx["state"]["respuesta"].lower()
    assert ctx["state"].get("fundamentada") is False or any(
        t in respuesta for t in ("no encontr", "no hay", "sin datos", "no existe")
    )


@then("no inventa un número")
def _no_inventa(ctx: dict):
    assert ctx["state"].get("fundamentada") is False


@then("el agente no ejecuta ninguna operación de escritura")
def _no_escribe(ctx: dict):
    sql = ctx["state"].get("sql_generado")
    # No debe haberse generado/ejecutado un SQL de escritura.
    assert sql is None or sql.strip().upper().startswith(("SELECT", "WITH"))


@then("explica que solo puede realizar consultas de lectura")
def _explica_lectura(ctx: dict):
    respuesta = ctx["state"]["respuesta"].lower()
    assert any(t in respuesta for t in ("lectura", "solo puedo", "consultas", "read"))
