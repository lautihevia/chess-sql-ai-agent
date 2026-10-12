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
| `fide_id` | INT | sí | FIDE ID de la persona (identificador oficial de la FIDE) | único; `NULL` en los jugadores sintéticos y en Alireza Firouzja (no se pudo verificar); ej. 1503014 |

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

## `champions` — personas que jugaron un campeonato mundial (datos reales)

Una fila por persona (campeones y retadores, 44). Datos reales. **Fuentes:** los años de
nacimiento y muerte salen de **Wikidata** (la base de datos estructurada de Wikimedia, licencia
CC0; no del texto de Wikipedia) y el `fide_id`, de Wikidata contrastado con la ficha de cada
jugador en `ratings.fide.com`. **No tiene país**: Wikidata trae varias nacionalidades históricas
por persona (p. ej. Capablanca figura como "Spain" como país deportivo) y elegir una sería un
juicio, no un dato.

| Columna | Tipo | Nulo | Descripción | Valores válidos |
|---|---|---|---|---|
| `champion_id` | INT | no | Identificador | PK |
| `name` | TEXT | no | Nombre completo | único, ej. "Bobby Fischer" |
| `birth_year` | INT | no | Año de nacimiento | ej. 1943 |
| `death_year` | INT | sí | Año de fallecimiento | `NULL` si vive |
| `fide_id` | INT | sí | FIDE ID: es la clave que une la persona con `players.fide_id` | único; `NULL` en los 22 campeones sin FIDE ID verificado (los históricos anteriores al sistema de ratings y 3 que la web de la FIDE no confirmó); ej. 1503014 |
| `player_id` | INT | sí | Vínculo opcional con `players`, resuelto por `fide_id` | FK → `players`; 8 de 44, `NULL` el resto |

## `world_championships` — campeonatos mundiales (datos reales, 1886-2024)

Datos reales extraídos de `data/pdfs/list-of-world-chess-championships.pdf`, no parte del seed
sintético. Se cargan junto con `champions` con `uv run python -m chess_agent.db.championships`.

| Columna | Tipo | Nulo | Descripción | Valores válidos |
|---|---|---|---|---|
| `championship_id` | INT | no | Identificador | PK |
| `year` | INT | no | Año en que se jugó (si cruza año, el de inicio) | 1886–2024 |
| `location` | TEXT | sí | Sede | ciudades en inglés, ej. "Reykjavík" |
| `winner_id` | INT | no | Quien ganó o retuvo el título | FK → `champions` |
| `win_number` | INT | no | N-ésimo título de ese jugador (como numera la fuente) | 1 = primera vez que se coronó |
| `runner_up_id` | INT | no | Rival | FK → `champions` |
| `score` | TEXT | sí | Marcador, ganador primero | ej. "12½–8½"; `NULL` en 1975 (Fischer no jugó) |
| `title_line` | TEXT | no | Linaje del título | `main`, `classical` (PCA 1993-2004), `fide_split` (FIDE 1993-2005) |
| `format` | TEXT | no | Formato | `match`, `tournament`, `knockout` |

Para los nombres hay que unir con `champions` (dos veces si se quieren ganador y rival). Para
"campeón en el año X" hay que usar `title_line = 'main'` y tomar el último campeonato con
`year <= X`; entre 1993 y 2006 hubo dos títulos rivales (`classical` y `fide_split`).

## Reglas semánticas clave (para text-to-SQL)

- **"Ganó con blancas"** → `games.white_player_id = <jugador> AND result = '1-0'`.
- **"Ganó con negras"** → `games.black_player_id = <jugador> AND result = '0-1'`.
- **"Empató / hizo tablas"** → `result = '1/2-1/2'`.
- Para contar victorias totales de un jugador hay que considerar **ambos colores**.
- El mapeo completo lenguaje↔esquema está en [term-mapping.md](term-mapping.md).
