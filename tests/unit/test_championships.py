"""Integridad de los datos de `champions` / `world_championships` (sin BD: valida en memoria)."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from chess_agent.db import championships, seed
from chess_agent.db.championships import (
    _COLUMNS,
    CHAMPIONS,
    CHAMPIONSHIPS,
    PLAYER_WIKIDATA_IDS,
)

_IDX = {c: i for i, c in enumerate(_COLUMNS)}
_LINEAS = {"main", "classical", "fide_split"}
_FORMATOS = {"match", "tournament", "knockout"}
_SCHEMA = Path(championships.__file__).with_name("schema.sql")


def _col(nombre: str) -> list:
    return [fila[_IDX[nombre]] for fila in CHAMPIONSHIPS]


def test_todas_las_filas_tienen_todas_las_columnas():
    assert all(len(fila) == len(_COLUMNS) for fila in CHAMPIONSHIPS)


def test_valores_validos_de_title_line_y_format():
    assert set(_col("title_line")) <= _LINEAS
    assert set(_col("format")) <= _FORMATOS


def test_anios_en_rango_y_orden_cronologico_por_linea():
    anios = _col("year")
    assert min(anios) == 1886 and max(anios) <= 2030
    por_linea: dict[str, list[int]] = defaultdict(list)
    for fila in CHAMPIONSHIPS:
        por_linea[fila[_IDX["title_line"]]].append(fila[_IDX["year"]])
    for linea, ys in por_linea.items():
        assert ys == sorted(ys), f"la línea {linea!r} no está en orden cronológico"


def test_win_number_es_consecutivo_por_jugador():
    # Los títulos se numeran por jugador a través de las líneas (Karpov, Kasparov, Anand...):
    # nunca se repite un número y no hay huecos.
    vistos: dict[str, set[int]] = defaultdict(set)
    for fila in CHAMPIONSHIPS:
        jugador, n = fila[_IDX["winner"]], fila[_IDX["win_number"]]
        assert n not in vistos[jugador], f"{jugador} repite el título nº {n}"
        vistos[jugador].add(n)
    for jugador, nums in vistos.items():
        assert nums == set(range(1, max(nums) + 1)), f"{jugador} tiene huecos: {sorted(nums)}"


def test_datos_clave_conocidos():
    por_anio = {(f[_IDX["year"]], f[_IDX["title_line"]]): f for f in CHAMPIONSHIPS}
    assert por_anio[(1972, "main")][_IDX["winner"]] == "Bobby Fischer"
    assert por_anio[(1972, "main")][_IDX["runner_up"]] == "Boris Spassky"
    assert por_anio[(2024, "main")][_IDX["winner"]] == "Gukesh Dommaraju"
    assert max(_col("win_number")) == 6  # Lasker, Karpov y Kasparov llegan a 6


# --- champions ---


def test_cada_campeon_aparece_en_algun_campeonato_y_viceversa():
    nombres = {nombre for nombre, *_ in CHAMPIONS}
    usados = set(_col("winner")) | set(_col("runner_up"))
    assert nombres == usados, f"sin usar / sin definir: {nombres ^ usados}"


def test_champions_sin_duplicados_y_con_datos_validos():
    nombres = [nombre for nombre, *_ in CHAMPIONS]
    assert len(nombres) == len(set(nombres))
    for nombre, nacimiento, muerte, qid in CHAMPIONS:
        assert 1800 <= nacimiento <= 2010, nombre
        assert muerte is None or nacimiento < muerte, nombre
        assert re.fullmatch(r"Q\d+", qid), f"{nombre}: id de Wikidata inválido {qid!r}"


def test_los_campeones_ya_no_vivian_antes_de_ser_campeones():
    nac = {nombre: n for nombre, n, _, _ in CHAMPIONS}
    muerte = {nombre: m for nombre, _, m, _ in CHAMPIONS}
    for fila in CHAMPIONSHIPS:
        anio = fila[_IDX["year"]]
        for rol in ("winner", "runner_up"):
            nombre = fila[_IDX[rol]]
            assert nac[nombre] < anio, f"{nombre} no había nacido en {anio}"
            assert muerte[nombre] is None or muerte[nombre] >= anio, f"{nombre} ya había muerto"


# --- el DDL del módulo y el de schema.sql no deben divergir ---


def _normalizar(ddl: str) -> str:
    ddl = re.sub(r"--[^\n]*", "", ddl)  # comentarios
    ddl = re.sub(r"IF NOT EXISTS ", "", ddl)
    return re.sub(r"\s+", " ", ddl).strip().replace("( ", "(").replace(" )", ")")


def _create_tables(sql: str, tablas: tuple[str, ...]) -> dict[str, str]:
    out = {}
    for t in tablas:
        m = re.search(rf"CREATE TABLE (?:IF NOT EXISTS )?{t} \(.*?\n\);", sql, re.DOTALL)
        assert m, f"no se encontró CREATE TABLE {t}"
        out[t] = _normalizar(m.group(0))
    return out


def test_ddl_del_modulo_coincide_con_schema_sql():
    tablas = ("champions", "world_championships")
    assert _create_tables(championships._DDL, tablas) == _create_tables(
        _SCHEMA.read_text(encoding="utf-8"), tablas
    )


# --- vínculo champions <-> players por wikidata_id ---

_ENLACES_ESPERADOS = {
    "Magnus Carlsen",
    "Fabiano Caruana",
    "Ian Nepomniachtchi",
    "Ding Liren",
    "Viswanathan Anand",
    "Vladimir Kramnik",
    "Sergey Karjakin",
    "Gukesh Dommaraju",
}


def test_ids_de_jugadores_son_de_jugadores_reales_del_seed_y_unicos():
    reales = {nombre for nombre, *_ in seed.REAL_PLAYERS}
    assert set(PLAYER_WIKIDATA_IDS) == reales
    assert len(set(PLAYER_WIKIDATA_IDS.values())) == len(PLAYER_WIKIDATA_IDS)
    assert all(re.fullmatch(r"Q\d+", qid) for qid in PLAYER_WIKIDATA_IDS.values())


def test_ids_de_campeones_son_unicos():
    ids = [qid for *_, qid in CHAMPIONS]
    assert len(ids) == len(set(ids))


def test_enlaces_champions_players_son_los_esperados():
    # Fija cuáles campeones quedan vinculados a `players` (por wikidata_id): si cambia la lista
    # de jugadores o de campeones, este test obliga a revisar el vínculo en vez de romperse en
    # silencio.
    por_qid = {qid: nombre for nombre, qid in PLAYER_WIKIDATA_IDS.items()}
    enlazados = {nombre: por_qid[qid] for nombre, _, _, qid in CHAMPIONS if qid in por_qid}
    assert set(enlazados.values()) == _ENLACES_ESPERADOS
    # Y el nombre del campeón coincide con el del jugador (misma persona, mismo nombre).
    assert all(campeon == jugador for campeon, jugador in enlazados.items())
