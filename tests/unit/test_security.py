"""Pruebas de seguridad (T033).

Aunque un intento de inyección de prompt logre que el LLM proponga SQL malicioso, la ejecución
debe quedar bloqueada. Se verifican las dos capas de defensa (Principio II):
1. el validador SQL rechaza escrituras, DDL, múltiples sentencias e inyecciones;
2. la conexión a la BD es de solo lectura (defensa en profundidad).
"""

from __future__ import annotations

import pytest

from chess_agent.sql.validator import SqlValidationError, validate_sql

# SQL que una inyección de prompt podría intentar colar. Todos deben rechazarse.
PAYLOADS_MALICIOSOS = [
    "DROP TABLE players",
    "DELETE FROM games",
    "UPDATE players SET peak_rating = 9999",
    "TRUNCATE moves",
    "INSERT INTO players (player_id, name) VALUES (999, 'hacker')",
    "ALTER TABLE games ADD COLUMN hacked int",
    "GRANT ALL ON games TO public",
    # Sentencias apiladas (stacked queries)
    "SELECT * FROM players; DROP TABLE players",
    "SELECT 1; DELETE FROM games",
    "SELECT name FROM players WHERE 1=1; UPDATE players SET name='x'",
    # SELECT ... INTO (crea tabla = escritura)
    "SELECT * INTO evil FROM players",
    # Escritura oculta tras un comentario
    "SELECT * FROM players\n-- comentario\n; DROP TABLE games",
]


class TestValidadorBloqueaInyecciones:
    @pytest.mark.parametrize("payload", PAYLOADS_MALICIOSOS)
    def test_rechaza_payload_malicioso(self, payload):
        with pytest.raises(SqlValidationError):
            validate_sql(payload)

    def test_select_legitimo_pasa_y_recibe_limit(self):
        out = validate_sql("SELECT name FROM players WHERE country = 'Norway'")
        assert out.strip().upper().startswith("SELECT")
        assert "LIMIT" in out.upper()


class TestDefensaEnProfundidad:
    """La conexión a la BD debe rechazar escrituras aunque lleguen a ejecutarse."""

    def test_conexion_read_only_bloquea_escritura(self):
        import psycopg

        from chess_agent.db.client import run_read_query

        # PostgreSQL rechaza la escritura en una transacción de solo lectura.
        with pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
            run_read_query("CREATE TABLE _sec_probe (x int)")
