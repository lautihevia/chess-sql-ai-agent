# Modelo de datos

Dominio: **partidas de ajedrez**. Base relacional en PostgreSQL (Supabase). Seis tablas;
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

    PLAYERS {
        int player_id PK
        text name
        text country
        int birth_year
        text title
        int peak_rating
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
```

## Notas de diseño

- **`games`** es la tabla central: referencia jugadores (blancas y negras), apertura y torneo.
- **`moves`** guarda **una fila por media jugada (ply)** con un índice en `game_id` para que
  reconstruir una partida sea instantáneo. Ver [ADR 0003](../decisions/0003-moves-por-ply.md).
- **`player_ratings`** permite consultas de evolución temporal (series de tiempo).
- El detalle campo por campo, con tipos y valores válidos, está en el
  [diccionario de datos](data-dictionary.md).
