# Estrategia de datos sintéticos (seed)

Cómo se genera el volumen de datos que consumirá el agente. El enunciado exige **≥5 tablas**
con **≥15 registros cada una**; acá se supera con holgura de forma coherente (respetando
claves foráneas y valores válidos).

## Enfoque

Generación **programática** con un script de seed en Python (posible apoyo de `Faker` para
nombres/fechas y de un catálogo real de aperturas ECO). El script es **idempotente y
reproducible** (semilla fija) para que cualquiera regenere los mismos datos.

## Volúmenes objetivo

| Tabla | Registros objetivo | Notas |
|---|---|---|
| `players` | ~30 | Mezcla de nombres reales conocidos + sintéticos, con títulos y ratings plausibles |
| `openings` | ~20 | Catálogo de aperturas con código ECO y primeras jugadas reales |
| `tournaments` | ~15 | Nombres, sedes, fechas y formato |
| `games` | ~150 | Referencian jugadores/apertura/torneo; resultado y nº de movimientos coherentes |
| `moves` | miles | ~1 fila por media jugada; generadas por partida (con índice en `game_id`) |
| `player_ratings` | ~200 | Historial mensual/anual por jugador para consultas de evolución |

## Reglas de coherencia

- Integridad referencial: toda FK apunta a un registro existente.
- `result` ∈ {`1-0`, `0-1`, `1/2-1/2`}; `color` ∈ {`white`, `black`}.
- `num_moves` de `games` consistente con la cantidad de filas en `moves` de esa partida.
- Blancas y negras de una partida son jugadores distintos.
- Ratings dentro de rangos realistas (~2200–2900).

## Realismo suficiente

No se busca precisión histórica total, sino que las **consultas sean significativas**:
distribución variada de resultados, aperturas y torneos para que rankings, conteos y
agregaciones den resultados interesantes (y verificables contra las
[golden queries](../agent/golden-queries.md)).

## Artefactos

- Script de seed (se agrega al implementar).
- Esquema SQL (`CREATE TABLE` + índices), base del [diccionario de datos](data-dictionary.md).
- Los datos generados se documentan como parte de los entregables (reproducibilidad).
