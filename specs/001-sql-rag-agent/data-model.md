# Modelo de datos (Fase 1)

Entidades derivadas de la spec. El detalle completo (tipos y valores válidos) vive en
[`docs/data/data-dictionary.md`](../../docs/data/data-dictionary.md) y el diagrama ER en
[`docs/data/data-model.md`](../../docs/data/data-model.md). Acá se resume para el plan.

## Entidades y campos

| Entidad | Campos | Relaciones |
|---|---|---|
| **players** | player_id (PK), name, country, birth_year, title, peak_rating | 1—N con games (blancas/negras) y player_ratings |
| **openings** | opening_id (PK), eco_code, name, first_moves | 1—N con games |
| **tournaments** | tournament_id (PK), name, location, country, start_date, end_date, format | 1—N con games |
| **games** | game_id (PK), tournament_id (FK), white_player_id (FK), black_player_id (FK), opening_id (FK), result, num_moves, date, round | N—1 con players/openings/tournaments; 1—N con moves |
| **moves** | move_id (PK), game_id (FK, indexado), move_number, color, san | N—1 con games |
| **player_ratings** | rating_id (PK), player_id (FK), rating_date, rating | N—1 con players |

## Reglas de validación (de los requisitos)

- `result` ∈ {`1-0`, `0-1`, `1/2-1/2`} (RF-003, seguridad de valores).
- `color` ∈ {`white`, `black`}.
- Toda FK referencia un registro existente (integridad referencial).
- Blancas y negras de una misma partida son jugadores distintos.
- `num_moves` de una partida es consistente con la cantidad de filas en `moves`.
- Volúmenes mínimos: ≥5 tablas con ≥15 registros (ver
  [`docs/data/seed-strategy.md`](../../docs/data/seed-strategy.md)).

## Acceso

El agente accede en **solo lectura** (Principio II). Índice en `moves.game_id` para reconstruir
partidas de forma eficiente (ADR 0003).
