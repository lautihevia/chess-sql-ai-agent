"""Pruebas del validador SQL (guardrails de solo lectura) — T012.

Escritas antes de la implementación (test-first, Principio III). Definen el contrato de
`validate_sql`: acepta un único SELECT, rechaza escrituras y múltiples sentencias, y agrega
un LIMIT de seguridad cuando falta.
"""

from __future__ import annotations

import pytest

from chess_agent.sql.validator import DEFAULT_MAX_LIMIT, SqlValidationError, validate_sql


class TestAceptaSelect:
    def test_select_simple_se_acepta(self):
        out = validate_sql("SELECT name FROM players WHERE country = 'Norway'")
        assert out.strip().upper().startswith("SELECT")

    def test_agrega_limit_si_falta(self):
        out = validate_sql("SELECT name FROM players")
        assert "LIMIT" in out.upper()
        assert str(DEFAULT_MAX_LIMIT) in out

    def test_respeta_limit_existente(self):
        out = validate_sql("SELECT name FROM players LIMIT 5")
        # No debe duplicar el LIMIT.
        assert out.upper().count("LIMIT") == 1

    def test_acepta_cte_with(self):
        out = validate_sql("WITH t AS (SELECT 1 AS n) SELECT n FROM t")
        assert "LIMIT" in out.upper()

    def test_quita_punto_y_coma_final(self):
        out = validate_sql("SELECT 1;")
        assert ";" not in out


class TestRechazaEscrituras:
    @pytest.mark.parametrize(
        "sql",
        [
            "INSERT INTO players (name) VALUES ('x')",
            "UPDATE players SET name = 'x'",
            "DELETE FROM games",
            "DROP TABLE games",
            "ALTER TABLE games ADD COLUMN x int",
            "TRUNCATE moves",
            "CREATE TABLE hack (x int)",
            "GRANT ALL ON games TO public",
        ],
    )
    def test_rechaza_dml_ddl(self, sql):
        with pytest.raises(SqlValidationError):
            validate_sql(sql)


class TestRechazaMultiplesSentencias:
    def test_rechaza_dos_selects(self):
        with pytest.raises(SqlValidationError):
            validate_sql("SELECT 1; SELECT 2")

    def test_rechaza_select_mas_escritura(self):
        with pytest.raises(SqlValidationError):
            validate_sql("SELECT 1; DROP TABLE games")


class TestEntradasInvalidas:
    @pytest.mark.parametrize("sql", ["", "   ", "NO_SQL", "los jugadores de Noruega"])
    def test_rechaza_no_select(self, sql):
        with pytest.raises(SqlValidationError):
            validate_sql(sql)
