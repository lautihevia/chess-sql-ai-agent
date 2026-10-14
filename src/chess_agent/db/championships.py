"""Tablas `champions` y `world_championships`: campeonatos mundiales de ajedrez (1886-2024).

Los campeonatos salen de `data/pdfs/list-of-world-chess-championships.pdf` (artículo de
Wikipedia, CC BY-SA); los años de nacimiento y muerte de cada persona, de Wikidata (CC0), y el
FIDE ID, de Wikidata contrastado con la ficha de ratings.fide.com. Son datos reales (a
diferencia del resto del seed, que es sintético). Las preguntas del tipo "¿quién fue campeón en
1972?" son de datos, y el RAG las resolvía mal porque el PDF deja las tablas partidas en líneas.

Relaciones:
    world_championships.winner_id / runner_up_id -> champions.champion_id
    champions.player_id -> players.player_id   (opcional: solo si la persona está en `players`;
                                                 hoy 8 de 44)

El vínculo entre `champions` y `players` se hace por **FIDE ID** (`fide_id` en ambas tablas),
no por nombre: los nombres son texto libre y no hay un estándar (la FIDE llama "Gukesh D" a quien
el PDF llama "Gukesh Dommaraju"). Los campeones históricos sin FIDE ID quedan sin vínculo.

No se guarda el país: Wikidata trae varias nacionalidades históricas por persona (p. ej.
Capablanca figura como "Spain" como país deportivo) y elegir una sería un juicio, no un dato.

Se puede cargar de forma independiente (requiere `players` ya cargada; recrea solo estas dos
tablas):

    uv run python -m chess_agent.db.championships

`seed.py` también las carga al regenerar la base completa.

Columnas de cada fila de `CHAMPIONSHIPS` (en orden de `_COLUMNS`):
    year          año en que se jugó (en matches que cruzan año, el de inicio)
    location      sede (ciudades, en inglés)
    winner        quien ganó o retuvo el título (nombre; se resuelve a `champions` al cargar)
    win_number    n-ésimo título de ese jugador, como numera la fuente (Karpov (6), etc.)
    runner_up     rival (nombre; se resuelve a `champions` al cargar)
    score         marcador (ganador primero); None si no hubo match
    title_line    'main' = linaje principal (privado hasta 1946, FIDE desde 1948, reunificado
                  desde 2006), 'classical' = título clásico PCA 1993-2004,
                  'fide_split' = título FIDE durante el cisma 1993-2005
    format        'match' | 'tournament' | 'knockout'
"""

from __future__ import annotations

from typing import Any

from chess_agent.db.client import connect

_COLUMNS = (
    "year", "location", "winner", "win_number", "runner_up", "score", "title_line", "format",
)

_DDL = """
CREATE TABLE champions (
    champion_id INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL UNIQUE,
    birth_year  INTEGER NOT NULL,
    death_year  INTEGER,
    fide_id     INTEGER UNIQUE,
    player_id   INTEGER REFERENCES players (player_id)
);

CREATE TABLE world_championships (
    championship_id INTEGER PRIMARY KEY,
    year            INTEGER NOT NULL,
    location        TEXT,
    winner_id       INTEGER NOT NULL REFERENCES champions (champion_id),
    win_number      INTEGER NOT NULL,
    runner_up_id    INTEGER NOT NULL REFERENCES champions (champion_id),
    score           TEXT,
    title_line      TEXT    NOT NULL CHECK (title_line IN ('main', 'classical', 'fide_split')),
    format          TEXT    NOT NULL CHECK (format IN ('match', 'tournament', 'knockout'))
);
"""

# FIDE ID de los jugadores reales de `players` (seed.REAL_PLAYERS). Cada id se tomó de Wikidata
# (propiedad P1440) y se verificó contra la ficha en ratings.fide.com (el nombre coincide).
# `players.fide_id` es NULL en los jugadores sintéticos.
PLAYER_FIDE_IDS: dict[str, int] = {
    "Magnus Carlsen": 1503014,
    "Hikaru Nakamura": 2016192,
    "Fabiano Caruana": 2020009,
    "Ian Nepomniachtchi": 4168119,
    "Ding Liren": 8603677,
    "Alireza Firouzja": 12573981,
    "Wesley So": 5202213,
    "Anish Giri": 24116068,
    "Levon Aronian": 13300474,
    "Viswanathan Anand": 5000017,
    "Vladimir Kramnik": 4101588,
    "Maxime Vachier-Lagrave": 623539,
    "Sergey Karjakin": 14109603,
    "Judit Polgar": 700070,
    "Hou Yifan": 8602980,
    "Teimour Radjabov": 13400924,
    "Shakhriyar Mamedyarov": 13401319,
    "Richard Rapport": 738590,
    "Gukesh Dommaraju": 46616543,
    "Rameshbabu Praggnanandhaa": 25059530,
}

# Personas (nombre, año de nacimiento, año de muerte o None, FIDE ID o None), en orden de primera
# aparición en CHAMPIONSHIPS. Nacimiento y muerte: Wikidata (propiedades P569 y P570). FIDE ID: solo
# si Wikidata lo tiene (P1440) y la ficha de ratings.fide.com coincide con el nombre. Quedan en None
# los campeones históricos anteriores al sistema de ratings y los fallecidos cuya ficha la FIDE ya
# no sirve ("No record found": Spassky, Timman y Korchnoi), aunque Wikidata tenga un id.
CHAMPIONS: list[tuple[str, int, int | None, int | None]] = [
    ("Wilhelm Steinitz", 1836, 1900, None),
    ("Johannes Zukertort", 1842, 1888, None),
    ("Mikhail Chigorin", 1850, 1908, None),
    ("Isidor Gunsberg", 1854, 1930, None),
    ("Emanuel Lasker", 1868, 1941, None),
    ("Frank Marshall", 1877, 1944, None),
    ("Siegbert Tarrasch", 1862, 1934, None),
    ("Carl Schlechter", 1874, 1918, None),
    ("Dawid Janowski", 1868, 1927, None),
    ("José Raúl Capablanca", 1888, 1942, None),
    ("Alexander Alekhine", 1892, 1946, None),
    ("Efim Bogoljubow", 1889, 1952, None),
    ("Max Euwe", 1901, 1981, None),
    ("Mikhail Botvinnik", 1911, 1995, None),
    ("Vasily Smyslov", 1921, 2010, None),
    ("David Bronstein", 1924, 2006, None),
    ("Mikhail Tal", 1936, 1992, None),
    ("Tigran Petrosian", 1929, 1984, None),
    ("Boris Spassky", 1937, 2025, None),
    ("Bobby Fischer", 1943, 2008, None),
    ("Anatoly Karpov", 1951, None, 4100026),
    ("Viktor Korchnoi", 1931, 2016, None),
    ("Garry Kasparov", 1963, None, 4100018),
    ("Nigel Short", 1965, None, 400025),
    ("Viswanathan Anand", 1969, None, 5000017),
    ("Vladimir Kramnik", 1975, None, 4101588),
    ("Peter Leko", 1979, None, 703303),
    ("Jan Timman", 1951, 2026, None),
    ("Gata Kamsky", 1974, None, 2000024),
    ("Alexander Khalifman", 1966, None, 4100115),
    ("Vladimir Akopian", 1971, None, 13300032),
    ("Alexei Shirov", 1972, None, 2209390),
    ("Ruslan Ponomariov", 1983, None, 14103320),
    ("Vasyl Ivanchuk", 1969, None, 14100010),
    ("Rustam Kasimdzhanov", 1979, None, 14200244),
    ("Michael Adams", 1971, None, 400041),
    ("Veselin Topalov", 1975, None, 2900084),
    ("Boris Gelfand", 1968, None, 2805677),
    ("Magnus Carlsen", 1990, None, 1503014),
    ("Sergey Karjakin", 1990, None, 14109603),
    ("Fabiano Caruana", 1992, None, 2020009),
    ("Ian Nepomniachtchi", 1990, None, 4168119),
    ("Ding Liren", 1992, None, 8603677),
    ("Gukesh Dommaraju", 2006, None, 46616543),
]

# fmt: off
CHAMPIONSHIPS: list[tuple[Any, ...]] = [
    # --- Matches organizados en forma privada (1886-1946) ---
    (1886, "New York City, St. Louis, New Orleans", "Wilhelm Steinitz", 1, "Johannes Zukertort", "12½–7½", "main", "match"),
    (1889, "Havana", "Wilhelm Steinitz", 2, "Mikhail Chigorin", "10½–6½", "main", "match"),
    (1890, "New York City", "Wilhelm Steinitz", 3, "Isidor Gunsberg", "10½–8½", "main", "match"),
    (1892, "Havana", "Wilhelm Steinitz", 4, "Mikhail Chigorin", "12½–10½", "main", "match"),
    (1894, "New York City, Philadelphia, Montréal", "Emanuel Lasker", 1, "Wilhelm Steinitz", "12–7", "main", "match"),
    (1896, "Moscow", "Emanuel Lasker", 2, "Wilhelm Steinitz", "12½–4½", "main", "match"),
    (1907, "New York City, Philadelphia, Washington, Baltimore, Chicago, Memphis", "Emanuel Lasker", 3, "Frank Marshall", "11½–3½", "main", "match"),
    (1908, "Düsseldorf, Munich", "Emanuel Lasker", 4, "Siegbert Tarrasch", "10½–5½", "main", "match"),
    (1910, "Vienna, Berlin", "Emanuel Lasker", 5, "Carl Schlechter", "5–5", "main", "match"),
    (1910, "Berlin", "Emanuel Lasker", 6, "Dawid Janowski", "9½–1½", "main", "match"),
    (1921, "Havana", "José Raúl Capablanca", 1, "Emanuel Lasker", "9–5", "main", "match"),
    (1927, "Buenos Aires", "Alexander Alekhine", 1, "José Raúl Capablanca", "18½–15½", "main", "match"),
    (1929, "Wiesbaden, Heidelberg, Berlin, The Hague, Rotterdam, Amsterdam", "Alexander Alekhine", 2, "Efim Bogoljubow", "15½–9½", "main", "match"),
    (1934, "12 cities in Germany", "Alexander Alekhine", 3, "Efim Bogoljubow", "15½–10½", "main", "match"),
    (1935, "12 cities in the Netherlands", "Max Euwe", 1, "Alexander Alekhine", "15½–14½", "main", "match"),
    (1937, "9 cities in the Netherlands", "Alexander Alekhine", 4, "Max Euwe", "15½–9½", "main", "match"),
    # --- Campeonatos FIDE (1948-1990) ---
    (1948, "The Hague, Moscow", "Mikhail Botvinnik", 1, "Vasily Smyslov", "14–6", "main", "tournament"),
    (1951, "Moscow", "Mikhail Botvinnik", 2, "David Bronstein", "12–12", "main", "match"),
    (1954, "Moscow", "Mikhail Botvinnik", 3, "Vasily Smyslov", "12–12", "main", "match"),
    (1957, "Moscow", "Vasily Smyslov", 1, "Mikhail Botvinnik", "12½–9½", "main", "match"),
    (1958, "Moscow", "Mikhail Botvinnik", 4, "Vasily Smyslov", "12½–10½", "main", "match"),
    (1960, "Moscow", "Mikhail Tal", 1, "Mikhail Botvinnik", "12½–8½", "main", "match"),
    (1961, "Moscow", "Mikhail Botvinnik", 5, "Mikhail Tal", "13–8", "main", "match"),
    (1963, "Moscow", "Tigran Petrosian", 1, "Mikhail Botvinnik", "12½–9½", "main", "match"),
    (1966, "Moscow", "Tigran Petrosian", 2, "Boris Spassky", "12½–11½", "main", "match"),
    (1969, "Moscow", "Boris Spassky", 1, "Tigran Petrosian", "12½–10½", "main", "match"),
    (1972, "Reykjavík", "Bobby Fischer", 1, "Boris Spassky", "12½–8½", "main", "match"),
    (1975, "Manila", "Anatoly Karpov", 1, "Bobby Fischer", None, "main", "match"),
    (1978, "Baguio", "Anatoly Karpov", 2, "Viktor Korchnoi", "16½–15½", "main", "match"),
    (1981, "Merano", "Anatoly Karpov", 3, "Viktor Korchnoi", "11–7", "main", "match"),
    (1985, "Moscow", "Garry Kasparov", 1, "Anatoly Karpov", "13–11", "main", "match"),
    (1986, "London, Leningrad", "Garry Kasparov", 2, "Anatoly Karpov", "12½–11½", "main", "match"),
    (1987, "Seville", "Garry Kasparov", 3, "Anatoly Karpov", "12–12", "main", "match"),
    (1990, "New York City, Lyon", "Garry Kasparov", 4, "Anatoly Karpov", "12½–11½", "main", "match"),
    # --- Cisma 1993-2006: campeonato clásico (PCA) ---
    (1993, "London", "Garry Kasparov", 5, "Nigel Short", "12½–7½", "classical", "match"),
    (1995, "New York City", "Garry Kasparov", 6, "Viswanathan Anand", "10½–7½", "classical", "match"),
    (2000, "London", "Vladimir Kramnik", 1, "Garry Kasparov", "8½–6½", "classical", "match"),
    (2004, "Brissago", "Vladimir Kramnik", 2, "Peter Leko", "7–7", "classical", "match"),
    # --- Cisma 1993-2006: campeonato FIDE ---
    (1993, "Zwolle, Arnhem, Amsterdam, Jakarta", "Anatoly Karpov", 4, "Jan Timman", "12½–8½", "fide_split", "match"),
    (1996, "Elista", "Anatoly Karpov", 5, "Gata Kamsky", "10½–7½", "fide_split", "match"),
    (1998, "Lausanne", "Anatoly Karpov", 6, "Viswanathan Anand", "3–3 (tiebreak 2–0)", "fide_split", "knockout"),
    (1999, "Las Vegas", "Alexander Khalifman", 1, "Vladimir Akopian", "3½–2½", "fide_split", "knockout"),
    (2000, "New Delhi, Tehran", "Viswanathan Anand", 1, "Alexei Shirov", "3½–½", "fide_split", "knockout"),
    (2002, "Moscow", "Ruslan Ponomariov", 1, "Vasyl Ivanchuk", "4½–2½", "fide_split", "knockout"),
    (2004, "Tripoli", "Rustam Kasimdzhanov", 1, "Michael Adams", "4½–3½", "fide_split", "knockout"),
    (2005, "Potrero de los Funes", "Veselin Topalov", 1, "Viswanathan Anand", "10–4", "fide_split", "tournament"),
    # --- Título reunificado (2006 en adelante) ---
    (2006, "Elista", "Vladimir Kramnik", 3, "Veselin Topalov", "6–6 (tiebreak 2½–1½)", "main", "match"),
    (2007, "Mexico City", "Viswanathan Anand", 2, "Vladimir Kramnik", "9–5", "main", "tournament"),
    (2008, "Bonn", "Viswanathan Anand", 3, "Vladimir Kramnik", "6½–4½", "main", "match"),
    (2010, "Sofia", "Viswanathan Anand", 4, "Veselin Topalov", "6½–5½", "main", "match"),
    (2012, "Moscow", "Viswanathan Anand", 5, "Boris Gelfand", "6–6 (tiebreak 2½–1½)", "main", "match"),
    (2013, "Chennai", "Magnus Carlsen", 1, "Viswanathan Anand", "6½–3½", "main", "match"),
    (2014, "Sochi", "Magnus Carlsen", 2, "Viswanathan Anand", "6½–4½", "main", "match"),
    (2016, "New York City", "Magnus Carlsen", 3, "Sergey Karjakin", "6–6 (tiebreak 3–1)", "main", "match"),
    (2018, "London", "Magnus Carlsen", 4, "Fabiano Caruana", "6–6 (tiebreak 3–0)", "main", "match"),
    (2021, "Dubai", "Magnus Carlsen", 5, "Ian Nepomniachtchi", "7½–3½", "main", "match"),
    (2023, "Astana", "Ding Liren", 1, "Ian Nepomniachtchi", "7–7 (tiebreak 2½–1½)", "main", "match"),
    (2024, "Singapore", "Gukesh Dommaraju", 1, "Ding Liren", "7½–6½", "main", "match"),
]
# fmt: on


def _prepare_players(cur) -> None:
    """Garantiza `players.fide_id` en bases creadas antes de que existiera la columna.

    Idempotente. En una base nueva la columna ya viene de `schema.sql` y `seed.py` la completa;
    esto solo agrega la columna y rellena los ids de los jugadores reales (por nombre, una única
    vez, porque `seed.py` insertó esos nombres desde la misma lista) en bases ya cargadas, y quita
    la columna `wikidata_id` de una versión anterior.
    """
    cur.execute("ALTER TABLE players DROP COLUMN IF EXISTS wikidata_id")
    cur.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS fide_id INTEGER UNIQUE")
    cur.executemany(
        "UPDATE players SET fide_id = %s WHERE name = %s AND fide_id IS NULL",
        [(fide, nombre) for nombre, fide in PLAYER_FIDE_IDS.items()],
    )


def replace_all(cur) -> tuple[int, int]:
    """Recrea y carga `champions` y `world_championships` con el cursor dado.

    Devuelve `(personas, campeonatos)`. Requiere que `players` exista (por la FK opcional).
    """
    _prepare_players(cur)
    cur.execute("DROP TABLE IF EXISTS world_championships CASCADE")
    cur.execute("DROP TABLE IF EXISTS champions CASCADE")
    cur.execute(_DDL)

    ids = {nombre: i for i, (nombre, *_) in enumerate(CHAMPIONS, start=1)}
    cur.executemany(
        "INSERT INTO champions (champion_id, name, birth_year, death_year, fide_id)"
        " VALUES (%s, %s, %s, %s, %s)",
        [(ids[nombre], nombre, nac, muerte, fide) for nombre, nac, muerte, fide in CHAMPIONS],
    )
    # Vínculo opcional con `players`, por FIDE ID (sin inventar jugadores).
    cur.execute(
        "UPDATE champions c SET player_id = p.player_id FROM players p"
        " WHERE p.fide_id = c.fide_id"
    )

    iw, ir = _COLUMNS.index("winner"), _COLUMNS.index("runner_up")
    filas = []
    for n, fila in enumerate(CHAMPIONSHIPS, start=1):
        fila = list(fila)
        fila[iw], fila[ir] = ids[fila[iw]], ids[fila[ir]]
        filas.append((n, *fila))
    cur.executemany(
        "INSERT INTO world_championships (championship_id, year, location, winner_id,"
        " win_number, runner_up_id, score, title_line, format)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        filas,
    )
    return len(CHAMPIONS), len(CHAMPIONSHIPS)


def load() -> tuple[int, int]:
    """Recrea y recarga las dos tablas, sin tocar el resto de la base."""
    with connect(read_only=False) as conn, conn.cursor() as cur:
        conteo = replace_all(cur)
        conn.commit()
    return conteo


if __name__ == "__main__":
    personas, campeonatos = load()
    print(f"champions: {personas} filas | world_championships: {campeonatos} filas")
