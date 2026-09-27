# Mapeo de términos (lenguaje natural → esquema)

Traducción de expresiones habituales del usuario (en español e inglés) a columnas y valores
del esquema. Se inyecta en el prompt del [nodo SQL](../agent/prompts/sql.md) para reducir
ambigüedad y evitar que el LLM adivine.

## Resultados

| El usuario dice… | Significa en el esquema |
|---|---|
| "ganó con blancas" / "won with white" | `white_player_id = <jugador> AND result = '1-0'` |
| "ganó con negras" / "won with black" | `black_player_id = <jugador> AND result = '0-1'` |
| "ganó" (total) | victorias con blancas (`result='1-0'`) **o** con negras (`result='0-1'`) según el color en cada partida |
| "perdió" | inverso del resultado según el color |
| "empató" / "hizo tablas" / "draw" | `result = '1/2-1/2'` |

## Entidades

| El usuario dice… | Tabla / columna |
|---|---|
| "jugador", "player", nombre propio | `players.name` |
| "blancas" / "white" | `games.white_player_id` |
| "negras" / "black" | `games.black_player_id` |
| "rating", "ELO", "puntaje" | `players.peak_rating` o `player_ratings.rating` (según si pregunta por el máximo o por evolución) |
| "título", "GM", "Gran Maestro", "grandmaster" | `players.title` |
| "país", "country", "de Noruega" | `players.country` / `tournaments.country` |
| "apertura", "opening", "Siciliana" | `openings.name` (usar `ILIKE '%...%'`) |
| "código ECO" | `openings.eco_code` |
| "torneo", "tournament" | `tournaments.name` |
| "ronda", "round" | `games.round` |
| "jugada", "movimiento", "move" | `moves.san` / `moves.move_number` |

## Convenciones

- Comparaciones de nombres de apertura o jugador: preferir `ILIKE '%texto%'` para tolerar
  variantes.
- "más/menos", "top N", "el mayor/menor" → `ORDER BY ... DESC/ASC LIMIT N`.
- "promedio/average" → `AVG(...)`; "cantidad/cuántos" → `COUNT(*)`.
- Fechas: formato `YYYY-MM-DD`.

Valores válidos completos: ver [diccionario de datos](data-dictionary.md).
