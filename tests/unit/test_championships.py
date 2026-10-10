"""Integridad de los datos de `world_championships` (sin BD: valida la tabla en memoria)."""

from __future__ import annotations

from collections import defaultdict

from chess_agent.db.championships import _COLUMNS, CHAMPIONSHIPS

_IDX = {c: i for i, c in enumerate(_COLUMNS)}
_LINEAS = {"main", "classical", "fide_split"}
_FORMATOS = {"match", "tournament", "knockout"}


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
    # Karpov (y Kasparov) acumulan títulos entre líneas, así que se cuenta por jugador en
    # el orden de la tabla *dentro* de cada línea cronológica: nunca se repite un número.
    vistos: dict[str, set[int]] = defaultdict(set)
    for fila in CHAMPIONSHIPS:
        jugador, n = fila[_IDX["winner"]], fila[_IDX["win_number"]]
        assert n not in vistos[jugador], f"{jugador} repite el título nº {n}"
        vistos[jugador].add(n)
    for jugador, nums in vistos.items():
        assert nums == set(range(1, max(nums) + 1)), f"{jugador} tiene huecos: {sorted(nums)}"


def test_datos_clave_conocidos():
    por_anio = {
        (f[_IDX["year"]], f[_IDX["title_line"]]): f for f in CHAMPIONSHIPS
    }
    assert por_anio[(1972, "main")][_IDX["winner"]] == "Bobby Fischer"
    assert por_anio[(1972, "main")][_IDX["runner_up"]] == "Boris Spassky"
    assert por_anio[(2024, "main")][_IDX["winner"]] == "Gukesh Dommaraju"
    assert max(_col("win_number")) == 6  # Lasker, Karpov y Kasparov llegan a 6
