# Modelo de datos

Dominio: **partidas de ajedrez**. Base relacional en PostgreSQL (Supabase). Ocho tablas:
seis con datos sintéticos (semilla fija) y dos con datos reales de los campeonatos mundiales;
cumple el mínimo del enunciado (≥5 tablas, ≥15 registros por tabla) con holgura.

## Diagrama entidad-relación

```mermaid
erDiagram
    PLAYERS ||--o{ GAMES : "juega (blancas)"
    PLAYERS ||--o{ GAMES : "juega (negras)"
    PLAYERS ||--o{ PLAYER_RATINGS : "tiene historial"
    OPENINGS ||--o{ GAMES : "clasifica"
    TOURNAMENTS ||--o{ GAMES : "agrupa"
    GAMES ||--o{ MOVES : "contiene"
    CHAMPIONS ||--o{ WORLD_CHAMPIONSHIPS : "gana"
    CHAMPIONS ||--o{ WORLD_CHAMPIONSHIPS : "es rival en"
    PLAYERS |o--o| CHAMPIONS : "misma persona (por fide_id)"

    PLAYERS {
        int player_id PK
        text name
        text country
        int birth_year
        text title
        int peak_rating
        int fide_id "único, opcional"
    }
    OPENINGS {
        int opening_id PK
        text eco_code
        text name
        text first_moves
    }
    TOURNAMENTS {
        int tournament_id PK
        text name
        text location
        text country
        date start_date
        date end_date
        text format
    }
    GAMES {
        int game_id PK
        int tournament_id FK
        int white_player_id FK
        int black_player_id FK
        int opening_id FK
        text result
        int num_moves
        date date
        int round
    }
    MOVES {
        int move_id PK
        int game_id FK
        int move_number
        text color
        text san
    }
    PLAYER_RATINGS {
        int rating_id PK
        int player_id FK
        date rating_date
        int rating
    }
    CHAMPIONS {
        int champion_id PK
        text name
        int birth_year
        int death_year
        int fide_id "único, opcional"
        int player_id FK "opcional"
    }
    WORLD_CHAMPIONSHIPS {
        int championship_id PK
        int year
        text location
        int winner_id FK
        int win_number
        int runner_up_id FK
        text score
        text title_line
        text format
    }
```

## Notas de diseño

- **`games`** es la tabla central: referencia jugadores (blancas y negras), apertura y torneo.
- **`moves`** guarda **una fila por media jugada (ply)** con un índice en `game_id` para que
  reconstruir una partida sea instantáneo. Ver [ADR 0003](../decisions/0003-moves-por-ply.md).
- **`player_ratings`** permite consultas de evolución temporal (series de tiempo).
- **`champions` y `world_championships`** son **datos reales** (no sintéticos): los campeonatos
  salen de `data/pdfs/list-of-world-chess-championships.pdf` y los años de nacimiento y muerte,
  de Wikidata. `world_championships` referencia a
  `champions` dos veces (`winner_id`, `runner_up_id`); un mismo año puede tener varias
  filas en el cisma 1993-2006 (`title_line`: `main`, `classical`, `fide_split`).
- **`champions.player_id` es un vínculo opcional con `players`**, resuelto por **`fide_id`** (el
  FIDE ID, presente en ambas tablas) y no por nombre: los nombres son texto libre y no hay un
  estándar (la FIDE llama "Gukesh D" a quien el PDF llama "Gukesh Dommaraju"). Cada FIDE ID se
  tomó de Wikidata y se verificó contra la ficha en `ratings.fide.com`; los que no se pudieron
  verificar quedan en `NULL`. Se completa para 8 de 44 personas; los campeones históricos
  anteriores al sistema de ratings no tienen FIDE ID. No se inventaron jugadores sintéticos para
  los campeones históricos, que ensuciarían los datos de `games`. Tampoco se guarda el país: Wikidata trae
  varias nacionalidades históricas por persona y elegir una sería un juicio, no un dato.
- El detalle campo por campo, con tipos y valores válidos, está en el
  [diccionario de datos](data-dictionary.md).
