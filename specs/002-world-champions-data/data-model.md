# Modelo de datos (Fase 1)

Entidades derivadas de la [spec](spec.md). El detalle completo de columnas vive en
[`docs/data/data-dictionary.md`](../../docs/data/data-dictionary.md) y el diagrama ER en
[`docs/data/data-model.md`](../../docs/data/data-model.md).

## Entidades y campos

| Entidad | Campos | Relaciones |
|---|---|---|
| **champions** | champion_id (PK), name (único), birth_year, death_year, fide_id (único, opcional), player_id (FK opcional) | 1—N con world_championships (como ganador y como rival); N—1 opcional con players |
| **world_championships** | championship_id (PK), year, location, winner_id (FK), win_number, runner_up_id (FK), score, title_line, format | N—1 con champions (dos veces) |
| **players** (cambio) | + fide_id (único, opcional) | 1—N opcional con champions |

## Reglas de validación

- `title_line` ∈ {`main`, `classical`, `fide_split`}; `format` ∈ {`match`, `tournament`, `knockout`}.
- `win_number` es el n-ésimo título del ganador, sin repetir ni dejar huecos.
- `death_year` es `NULL` si la persona vive; el nacimiento es anterior a la muerte y al campeonato.
- `fide_id` es único; `NULL` en los campeones históricos anteriores al sistema de ratings y en los
  que la web de la FIDE ya no sirve por estar fallecidos (Spassky, Timman, Korchnoi).
- `champions.player_id` solo se completa si el FIDE ID coincide con el de un jugador (8 de 44).

## Fuente de cada dato

| Dato | Fuente |
|---|---|
| Campeonatos (año, sede, ganador, rival, marcador, línea, formato) | `data/pdfs/list-of-world-chess-championships.pdf` (Wikipedia, CC BY-SA) |
| Años de nacimiento y muerte | Wikidata (propiedades P569 y P570; CC0) |
| FIDE ID | Wikidata (P1440), contrastado con la ficha en `ratings.fide.com` |

## Transiciones de estado

No aplica: las tablas se cargan y recargan completas (`DELETE`/`DROP` + `INSERT`), sin estados.
