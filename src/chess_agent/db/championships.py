"""Tabla `world_championships`: historial de campeonatos mundiales de ajedrez (1886-2024).

Los datos salen de `data/pdfs/list-of-world-chess-championships.pdf` (artículo de Wikipedia,
CC BY-SA). Son datos reales (a diferencia del resto del seed, que es sintético) y viven en una
tabla propia: las preguntas del tipo "¿quién fue campeón en 1972?" son de datos, y el RAG las
resolvía mal porque el PDF deja las tablas partidas en líneas sueltas.

Se puede cargar de forma independiente, sin tocar las demás tablas (idempotente):

    uv run python -m chess_agent.db.championships

`seed.py` también la carga al regenerar la base completa.

Columnas de cada fila (en orden de `_COLUMNS`):
    year          año en que se jugó (en matches que cruzan año, el de inicio)
    location      sede (ciudades, en inglés)
    winner        quien ganó o retuvo el título
    win_number    n-ésimo título de ese jugador, como numera la fuente (Karpov (6), etc.)
    runner_up     rival
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
CREATE TABLE IF NOT EXISTS world_championships (
    championship_id INTEGER PRIMARY KEY,
    year            INTEGER NOT NULL,
    location        TEXT,
    winner          TEXT    NOT NULL,
    win_number      INTEGER NOT NULL,
    runner_up       TEXT    NOT NULL,
    score           TEXT,
    title_line      TEXT    NOT NULL CHECK (title_line IN ('main', 'classical', 'fide_split')),
    format          TEXT    NOT NULL CHECK (format IN ('match', 'tournament', 'knockout')),
    notes           TEXT
);
"""

_TIE = "Tied match: the champion retained the title."

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


def replace_all(cur) -> int:
    """Reemplaza el contenido de la tabla usando el cursor dado (misma transacción)."""
    cur.execute(_DDL)
    cur.execute("DELETE FROM world_championships")
    cur.executemany(
        "INSERT INTO world_championships (championship_id, "
        + ", ".join(_COLUMNS)
        + ") VALUES (%s"
        + ", %s" * len(_COLUMNS)
        + ")",
        [(i, *fila) for i, fila in enumerate(CHAMPIONSHIPS, start=1)],
    )
    return len(CHAMPIONSHIPS)


def load() -> int:
    """Crea la tabla si falta y la recarga, sin tocar el resto de la base."""
    with connect(read_only=False) as conn, conn.cursor() as cur:
        n = replace_all(cur)
        conn.commit()
    return n


if __name__ == "__main__":
    print(f"world_championships: {load()} filas cargadas")
