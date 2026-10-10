"""Tablas `champions` y `world_championships`: campeonatos mundiales de ajedrez (1886-2024).

Los campeonatos salen de `data/pdfs/list-of-world-chess-championships.pdf` (artículo de
Wikipedia, CC BY-SA); las fechas de nacimiento y muerte de cada persona, de Wikidata (CC0), cuyo
identificador queda en `champions.wikidata_id` para poder verificarlas. Son datos reales (a
diferencia del resto del seed, que es sintético). Las preguntas del tipo "¿quién fue campeón en
1972?" son de datos, y el RAG las resolvía mal porque el PDF deja las tablas partidas en líneas.

Relaciones:
    world_championships.winner_id / runner_up_id -> champions.champion_id
    champions.player_id -> players.player_id   (opcional: solo si la persona está en `players`,
                                                 es decir, coincide el nombre; hoy 8 de 44)

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
    notes         aclaraciones (empate que retiene el título, desempate, etc.)
"""

from __future__ import annotations

from typing import Any

from chess_agent.db.client import connect

_COLUMNS = (
    "year", "location", "winner", "win_number", "runner_up", "score", "title_line", "format",
    "notes",
)

_DDL = """
CREATE TABLE champions (
    champion_id INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL UNIQUE,
    birth_year  INTEGER NOT NULL,
    death_year  INTEGER,
    wikidata_id TEXT    NOT NULL,
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
    format          TEXT    NOT NULL CHECK (format IN ('match', 'tournament', 'knockout')),
    notes           TEXT
);
"""

_TIE = "Tied match: the champion retained the title."

# Personas (nombre, año de nacimiento, año de muerte o None, id de Wikidata), en orden de primera
# aparición en CHAMPIONSHIPS. Fuente: Wikidata (propiedades P569 y P570).
CHAMPIONS: list[tuple[str, int, int | None, str]] = [
    ("Wilhelm Steinitz", 1836, 1900, "Q102648"),
    ("Johannes Zukertort", 1842, 1888, "Q60182"),
    ("Mikhail Chigorin", 1850, 1908, "Q298286"),
    ("Isidor Gunsberg", 1854, 1930, "Q357796"),
    ("Emanuel Lasker", 1868, 1941, "Q57095"),
    ("Frank Marshall", 1877, 1944, "Q312814"),
    ("Siegbert Tarrasch", 1862, 1934, "Q76558"),
    ("Carl Schlechter", 1874, 1918, "Q320017"),
    ("Dawid Janowski", 1868, 1927, "Q378839"),
    ("José Raúl Capablanca", 1888, 1942, "Q160702"),
    ("Alexander Alekhine", 1892, 1946, "Q131374"),
    ("Efim Bogoljubow", 1889, 1952, "Q57310"),
    ("Max Euwe", 1901, 1981, "Q173714"),
    ("Mikhail Botvinnik", 1911, 1995, "Q178865"),
    ("Vasily Smyslov", 1921, 2010, "Q104148"),
    ("David Bronstein", 1924, 2006, "Q312908"),
    ("Mikhail Tal", 1936, 1992, "Q102664"),
    ("Tigran Petrosian", 1929, 1984, "Q180636"),
    ("Boris Spassky", 1937, 2025, "Q177310"),
    ("Bobby Fischer", 1943, 2008, "Q41314"),
    ("Anatoly Karpov", 1951, None, "Q131674"),
    ("Viktor Korchnoi", 1931, 2016, "Q212889"),
    ("Garry Kasparov", 1963, None, "Q28614"),
    ("Nigel Short", 1965, None, "Q313778"),
    ("Viswanathan Anand", 1969, None, "Q45747"),
    ("Vladimir Kramnik", 1975, None, "Q161092"),
    ("Peter Leko", 1979, None, "Q210922"),
    ("Jan Timman", 1951, 2026, "Q139438"),
    ("Gata Kamsky", 1974, None, "Q315155"),
    ("Alexander Khalifman", 1966, None, "Q106374"),
    ("Vladimir Akopian", 1971, None, "Q380839"),
    ("Alexei Shirov", 1972, None, "Q214713"),
    ("Ruslan Ponomariov", 1983, None, "Q207723"),
    ("Vasyl Ivanchuk", 1969, None, "Q208229"),
    ("Rustam Kasimdzhanov", 1979, None, "Q489015"),
    ("Michael Adams", 1971, None, "Q299636"),
    ("Veselin Topalov", 1975, None, "Q172798"),
    ("Boris Gelfand", 1968, None, "Q486778"),
    ("Magnus Carlsen", 1990, None, "Q106807"),
    ("Sergey Karjakin", 1990, None, "Q217198"),
    ("Fabiano Caruana", 1992, None, "Q367277"),
    ("Ian Nepomniachtchi", 1990, None, "Q521817"),
    ("Ding Liren", 1992, None, "Q1191198"),
    ("Gukesh Dommaraju", 2006, None, "Q56026072"),
]

# fmt: off
CHAMPIONSHIPS: list[tuple[Any, ...]] = [
    # --- Matches organizados en forma privada (1886-1946) ---
    (1886, "New York City, St. Louis, New Orleans", "Wilhelm Steinitz", 1, "Johannes Zukertort", "12½–7½", "main", "match", "First official World Championship."),
    (1889, "Havana", "Wilhelm Steinitz", 2, "Mikhail Chigorin", "10½–6½", "main", "match", None),
    (1890, "New York City", "Wilhelm Steinitz", 3, "Isidor Gunsberg", "10½–8½", "main", "match", "Played 1890-1891."),
    (1892, "Havana", "Wilhelm Steinitz", 4, "Mikhail Chigorin", "12½–10½", "main", "match", None),
    (1894, "New York City, Philadelphia, Montréal", "Emanuel Lasker", 1, "Wilhelm Steinitz", "12–7", "main", "match", "Lasker became champion."),
    (1896, "Moscow", "Emanuel Lasker", 2, "Wilhelm Steinitz", "12½–4½", "main", "match", "Played 1896-1897."),
    (1907, "New York City, Philadelphia, Washington, Baltimore, Chicago, Memphis", "Emanuel Lasker", 3, "Frank Marshall", "11½–3½", "main", "match", None),
    (1908, "Düsseldorf, Munich", "Emanuel Lasker", 4, "Siegbert Tarrasch", "10½–5½", "main", "match", None),
    (1910, "Vienna, Berlin", "Emanuel Lasker", 5, "Carl Schlechter", "5–5", "main", "match", "Played Jan-Feb 1910. " + _TIE),
    (1910, "Berlin", "Emanuel Lasker", 6, "Dawid Janowski", "9½–1½", "main", "match", "Played Nov-Dec 1910."),
    (1921, "Havana", "José Raúl Capablanca", 1, "Emanuel Lasker", "9–5", "main", "match", "Capablanca became champion."),
    (1927, "Buenos Aires", "Alexander Alekhine", 1, "José Raúl Capablanca", "18½–15½", "main", "match", "Alekhine became champion."),
    (1929, "Wiesbaden, Heidelberg, Berlin, The Hague, Rotterdam, Amsterdam", "Alexander Alekhine", 2, "Efim Bogoljubow", "15½–9½", "main", "match", None),
    (1934, "12 cities in Germany", "Alexander Alekhine", 3, "Efim Bogoljubow", "15½–10½", "main", "match", None),
    (1935, "12 cities in the Netherlands", "Max Euwe", 1, "Alexander Alekhine", "15½–14½", "main", "match", "Euwe became champion."),
    (1937, "9 cities in the Netherlands", "Alexander Alekhine", 4, "Max Euwe", "15½–9½", "main", "match", "Alekhine regained the title. The title was vacant from 1946 (death of Alekhine) to 1948."),
    # --- Campeonatos FIDE (1948-1990) ---
    (1948, "The Hague, Moscow", "Mikhail Botvinnik", 1, "Vasily Smyslov", "14–6", "main", "tournament", "Five-player quintuple round-robin tournament. First FIDE World Champion."),
    (1951, "Moscow", "Mikhail Botvinnik", 2, "David Bronstein", "12–12", "main", "match", _TIE),
    (1954, "Moscow", "Mikhail Botvinnik", 3, "Vasily Smyslov", "12–12", "main", "match", _TIE),
    (1957, "Moscow", "Vasily Smyslov", 1, "Mikhail Botvinnik", "12½–9½", "main", "match", "Smyslov became champion."),
    (1958, "Moscow", "Mikhail Botvinnik", 4, "Vasily Smyslov", "12½–10½", "main", "match", "Rematch: Botvinnik regained the title."),
    (1960, "Moscow", "Mikhail Tal", 1, "Mikhail Botvinnik", "12½–8½", "main", "match", "Tal became champion."),
    (1961, "Moscow", "Mikhail Botvinnik", 5, "Mikhail Tal", "13–8", "main", "match", "Rematch: Botvinnik regained the title."),
    (1963, "Moscow", "Tigran Petrosian", 1, "Mikhail Botvinnik", "12½–9½", "main", "match", "Petrosian became champion."),
    (1966, "Moscow", "Tigran Petrosian", 2, "Boris Spassky", "12½–11½", "main", "match", None),
    (1969, "Moscow", "Boris Spassky", 1, "Tigran Petrosian", "12½–10½", "main", "match", "Spassky became champion."),
    (1972, "Reykjavík", "Bobby Fischer", 1, "Boris Spassky", "12½–8½", "main", "match", "Fischer became champion; the only non-Soviet winner between 1948 and 1991."),
    (1975, "Manila", "Anatoly Karpov", 1, "Bobby Fischer", None, "main", "match", "No match was played: Fischer forfeited the title and FIDE declared Karpov champion by default."),
    (1978, "Baguio", "Anatoly Karpov", 2, "Viktor Korchnoi", "16½–15½", "main", "match", "First to 6 wins."),
    (1981, "Merano", "Anatoly Karpov", 3, "Viktor Korchnoi", "11–7", "main", "match", "First to 6 wins."),
    (1985, "Moscow", "Garry Kasparov", 1, "Anatoly Karpov", "13–11", "main", "match", "Kasparov became champion. Replaced the 1984-85 Karpov-Kasparov match, which FIDE ended with no result after 48 games."),
    (1986, "London, Leningrad", "Garry Kasparov", 2, "Anatoly Karpov", "12½–11½", "main", "match", None),
    (1987, "Seville", "Garry Kasparov", 3, "Anatoly Karpov", "12–12", "main", "match", _TIE),
    (1990, "New York City, Lyon", "Garry Kasparov", 4, "Anatoly Karpov", "12½–11½", "main", "match", None),
    # --- Cisma 1993-2006: campeonato clásico (PCA) ---
    (1993, "London", "Garry Kasparov", 5, "Nigel Short", "12½–7½", "classical", "match", "Professional Chess Association (PCA) title, created after Kasparov and Short split from FIDE."),
    (1995, "New York City", "Garry Kasparov", 6, "Viswanathan Anand", "10½–7½", "classical", "match", "PCA title."),
    (2000, "London", "Vladimir Kramnik", 1, "Garry Kasparov", "8½–6½", "classical", "match", "Kramnik became Classical champion."),
    (2004, "Brissago", "Vladimir Kramnik", 2, "Peter Leko", "7–7", "classical", "match", "Classical title. " + _TIE),
    # --- Cisma 1993-2006: campeonato FIDE ---
    (1993, "Zwolle, Arnhem, Amsterdam, Jakarta", "Anatoly Karpov", 4, "Jan Timman", "12½–8½", "fide_split", "match", "FIDE title; FIDE stripped Kasparov of the title."),
    (1996, "Elista", "Anatoly Karpov", 5, "Gata Kamsky", "10½–7½", "fide_split", "match", "FIDE title."),
    (1998, "Lausanne", "Anatoly Karpov", 6, "Viswanathan Anand", "3–3 (tiebreak 2–0)", "fide_split", "knockout", "FIDE title. 100-player single-elimination tournament; Karpov was seeded directly into the final."),
    (1999, "Las Vegas", "Alexander Khalifman", 1, "Vladimir Akopian", "3½–2½", "fide_split", "knockout", "FIDE title. Final score; aggregate over all rounds 18½–11½."),
    (2000, "New Delhi, Tehran", "Viswanathan Anand", 1, "Alexei Shirov", "3½–½", "fide_split", "knockout", "FIDE title. Final score; aggregate over all rounds 14–6."),
    (2002, "Moscow", "Ruslan Ponomariov", 1, "Vasyl Ivanchuk", "4½–2½", "fide_split", "knockout", "FIDE title. 128-player single-elimination tournament; final score, aggregate 19–9."),
    (2004, "Tripoli", "Rustam Kasimdzhanov", 1, "Michael Adams", "4½–3½", "fide_split", "knockout", "FIDE title. Final score; aggregate over all rounds 20–10."),
    (2005, "Potrero de los Funes", "Veselin Topalov", 1, "Viswanathan Anand", "10–4", "fide_split", "tournament", "FIDE title. Double round-robin tournament with 8 players."),
    # --- Título reunificado (2006 en adelante) ---
    (2006, "Elista", "Vladimir Kramnik", 3, "Veselin Topalov", "6–6 (tiebreak 2½–1½)", "main", "match", "Reunification match between the Classical and FIDE champions."),
    (2007, "Mexico City", "Viswanathan Anand", 2, "Vladimir Kramnik", "9–5", "main", "tournament", "Double round-robin tournament with 8 players."),
    (2008, "Bonn", "Viswanathan Anand", 3, "Vladimir Kramnik", "6½–4½", "main", "match", None),
    (2010, "Sofia", "Viswanathan Anand", 4, "Veselin Topalov", "6½–5½", "main", "match", None),
    (2012, "Moscow", "Viswanathan Anand", 5, "Boris Gelfand", "6–6 (tiebreak 2½–1½)", "main", "match", None),
    (2013, "Chennai", "Magnus Carlsen", 1, "Viswanathan Anand", "6½–3½", "main", "match", "Carlsen became champion."),
    (2014, "Sochi", "Magnus Carlsen", 2, "Viswanathan Anand", "6½–4½", "main", "match", None),
    (2016, "New York City", "Magnus Carlsen", 3, "Sergey Karjakin", "6–6 (tiebreak 3–1)", "main", "match", None),
    (2018, "London", "Magnus Carlsen", 4, "Fabiano Caruana", "6–6 (tiebreak 3–0)", "main", "match", "All 12 classical games were draws."),
    (2021, "Dubai", "Magnus Carlsen", 5, "Ian Nepomniachtchi", "7½–3½", "main", "match", "Carlsen declined to defend the title in 2023."),
    (2023, "Astana", "Ding Liren", 1, "Ian Nepomniachtchi", "7–7 (tiebreak 2½–1½)", "main", "match", "Ding Liren became champion; Carlsen did not defend the title."),
    (2024, "Singapore", "Gukesh Dommaraju", 1, "Ding Liren", "7½–6½", "main", "match", "Gukesh became champion at age 18."),
]
# fmt: on


def replace_all(cur) -> tuple[int, int]:
    """Recrea y carga `champions` y `world_championships` con el cursor dado.

    Devuelve `(personas, campeonatos)`. Requiere que `players` exista (por la FK opcional).
    """
    cur.execute("DROP TABLE IF EXISTS world_championships CASCADE")
    cur.execute("DROP TABLE IF EXISTS champions CASCADE")
    cur.execute(_DDL)

    ids = {nombre: i for i, (nombre, *_) in enumerate(CHAMPIONS, start=1)}
    cur.executemany(
        "INSERT INTO champions (champion_id, name, birth_year, death_year, wikidata_id)"
        " VALUES (%s, %s, %s, %s, %s)",
        [(ids[nombre], nombre, nac, muerte, qid) for nombre, nac, muerte, qid in CHAMPIONS],
    )
    # Vínculo opcional con `players`: solo donde el nombre coincide (sin inventar jugadores).
    cur.execute(
        "UPDATE champions c SET player_id = p.player_id FROM players p WHERE p.name = c.name"
    )

    iw, ir = _COLUMNS.index("winner"), _COLUMNS.index("runner_up")
    filas = []
    for n, fila in enumerate(CHAMPIONSHIPS, start=1):
        fila = list(fila)
        fila[iw], fila[ir] = ids[fila[iw]], ids[fila[ir]]
        filas.append((n, *fila))
    cur.executemany(
        "INSERT INTO world_championships (championship_id, year, location, winner_id,"
        " win_number, runner_up_id, score, title_line, format, notes)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
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
