# Diccionario de datos

Descripción autoritativa de cada tabla y columna. **Este documento es la fuente de verdad
del esquema para el nodo text-to-SQL**: se inyecta (o se deriva) en el prompt para que el
LLM genere SQL correcto y no invente columnas ni valores.

Convenciones: PK = clave primaria, FK = clave foránea. Todos los `*_id` son enteros.

## `players` — jugadores

| Columna | Tipo | Nulo | Descripción | Valores válidos |
|---|---|---|---|---|
| `player_id` | INT | no | Identificador | PK |
| `name` | TEXT | no | Nombre completo | ej. "Magnus Carlsen" |
| `country` | TEXT | sí | País | nombre en inglés, ej. "Norway" |
| `birth_year` | INT | sí | Año de nacimiento | ej. 1990 |
| `title` | TEXT | sí | Título FIDE | `GM`, `IM`, `FM`, `WGM`, `WIM`, `CM`, `NM`, o `NULL` |
| `peak_rating` | INT | sí | Máximo rating histórico | ej. 2882 |

## `openings` — aperturas

| Columna | Tipo | Nulo | Descripción | Valores válidos |
|---|---|---|---|---|
| `opening_id` | INT | no | Identificador | PK |
| `eco_code` | TEXT | no | Código ECO | `A00`–`E99`, ej. "B90" |
| `name` | TEXT | no | Nombre | ej. "Sicilian Defense, Najdorf" |
| `first_moves` | TEXT | sí | Primeras jugadas en SAN | ej. "1.e4 c5 2.Nf3 d6 3.d4" |

## `tournaments` — torneos

| Columna | Tipo | Nulo | Descripción | Valores válidos |
|---|---|---|---|---|
| `tournament_id` | INT | no | Identificador | PK |
| `name` | TEXT | no | Nombre | ej. "Tata Steel 2023" |
| `location` | TEXT | sí | Ciudad | ej. "Wijk aan Zee" |
| `country` | TEXT | sí | País | ej. "Netherlands" |
| `start_date` | DATE | sí | Fecha de inicio | `YYYY-MM-DD` |
| `end_date` | DATE | sí | Fecha de fin | `YYYY-MM-DD` |
| `format` | TEXT | sí | Formato | `round-robin`, `swiss`, `knockout` |

## `games` — partidas (tabla central)

| Columna | Tipo | Nulo | Descripción | Valores válidos |
|---|---|---|---|---|
| `game_id` | INT | no | Identificador | PK |
| `tournament_id` | INT | sí | Torneo | FK → `tournaments` |
| `white_player_id` | INT | no | Jugador de blancas | FK → `players` |
| `black_player_id` | INT | no | Jugador de negras | FK → `players` |
| `opening_id` | INT | sí | Apertura | FK → `openings` |
| `result` | TEXT | no | Resultado | **solo** `1-0`, `0-1`, `1/2-1/2` |
| `num_moves` | INT | sí | Cantidad de movimientos | ej. 41 |
| `date` | DATE | sí | Fecha de la partida | `YYYY-MM-DD` |
| `round` | INT | sí | Ronda dentro del torneo | ej. 7 |

## `moves` — jugadas (una fila por ply)

| Columna | Tipo | Nulo | Descripción | Valores válidos |
|---|---|---|---|---|
| `move_id` | INT | no | Identificador | PK |
| `game_id` | INT | no | Partida | FK → `games` (indexado) |
| `move_number` | INT | no | Número de movimiento | 1, 2, 3, … |
| `color` | TEXT | no | Color que jugó | `white`, `black` |
| `san` | TEXT | no | Jugada en notación SAN | ej. "Nf3", "O-O", "exd5" |

## `player_ratings` — historial de rating

| Columna | Tipo | Nulo | Descripción | Valores válidos |
|---|---|---|---|---|
| `rating_id` | INT | no | Identificador | PK |
| `player_id` | INT | no | Jugador | FK → `players` |
| `rating_date` | DATE | no | Fecha de la medición | `YYYY-MM-DD` |
| `rating` | INT | no | Rating en esa fecha | ej. 2850 |

## Reglas semánticas clave (para text-to-SQL)

- **"Ganó con blancas"** → `games.white_player_id = <jugador> AND result = '1-0'`.
- **"Ganó con negras"** → `games.black_player_id = <jugador> AND result = '0-1'`.
- **"Empató / hizo tablas"** → `result = '1/2-1/2'`.
- Para contar victorias totales de un jugador hay que considerar **ambos colores**.
- El mapeo completo lenguaje↔esquema está en [term-mapping.md](term-mapping.md).
