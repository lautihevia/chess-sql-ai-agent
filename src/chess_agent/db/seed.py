"""Seed de datos sintéticos, determinista y reproducible (Principio V).

Genera datos coherentes de ajedrez con una **semilla fija**: cualquiera que ejecute este script
obtiene exactamente la misma BD. Respeta la integridad referencial, los valores válidos
(`result`, `color`, `title`, `format`) y la consistencia `num_moves == filas en moves`.

Volúmenes (superan el mínimo del enunciado: ≥5 tablas con ≥15 registros):
    players ~30 · openings 20 · tournaments 15 · games 150 · player_ratings ~210 · moves ~miles

Uso:
    uv run python -m chess_agent.db.seed          # aplica schema + carga datos
"""

from __future__ import annotations

import datetime as dt
import random
from pathlib import Path

from chess_agent.db.client import connect

#Este archivo sirve para cargar los datos de prueba en supabase. Podria verse luego alguna mejor forma de cargar estas
#tablas con mas cantidad de datos, pero sirve por ahora.
SEED = 42
SCHEMA_PATH = Path(__file__).with_name("schema.sql")

TITLES = ["GM", "IM", "FM", "WGM", "WIM", "CM", "NM"]
RESULTS = ["1-0", "0-1", "1/2-1/2"]
FORMATS = ["round-robin", "swiss", "knockout"]

# Jugadores reales conocidos (datos plausibles, no necesariamente exactos).
REAL_PLAYERS = [
    ("Magnus Carlsen", "Norway", 1990, "GM", 2882),
    ("Hikaru Nakamura", "United States", 1987, "GM", 2816),
    ("Fabiano Caruana", "United States", 1992, "GM", 2844),
    ("Ian Nepomniachtchi", "Russia", 1990, "GM", 2795),
    ("Ding Liren", "China", 1992, "GM", 2816),
    ("Alireza Firouzja", "France", 2003, "GM", 2804),
    ("Wesley So", "United States", 1993, "GM", 2822),
    ("Anish Giri", "Netherlands", 1994, "GM", 2798),
    ("Levon Aronian", "United States", 1982, "GM", 2830),
    ("Viswanathan Anand", "India", 1969, "GM", 2817),
    ("Vladimir Kramnik", "Russia", 1975, "GM", 2817),
    ("Maxime Vachier-Lagrave", "France", 1990, "GM", 2819),
    ("Sergey Karjakin", "Russia", 1990, "GM", 2788),
    ("Judit Polgar", "Hungary", 1976, "GM", 2735),
    ("Hou Yifan", "China", 1994, "GM", 2686),
    ("Teimour Radjabov", "Azerbaijan", 1987, "GM", 2793),
    ("Shakhriyar Mamedyarov", "Azerbaijan", 1985, "GM", 2820),
    ("Richard Rapport", "Hungary", 1996, "GM", 2776),
    ("Gukesh Dommaraju", "India", 2006, "GM", 2794),
    ("Rameshbabu Praggnanandhaa", "India", 2005, "GM", 2758),
]

# Nombres sintéticos para completar el padrón.
SYNTH_FIRST = [
    "Marco", "Elena", "Pavel", "Sofia", "Diego", "Nadia", "Lukas", "Irina", "Tomas", "Lena",
]
SYNTH_LAST = ["Volkov", "Marino", "Kowalski", "Bauer", "Silva", "Novak", "Petrov", "Haas"]
COUNTRIES = ["Argentina", "Germany", "Poland", "Spain", "Brazil", "Serbia", "Ukraine", "Austria"]

# Catálogo de aperturas (ECO real).
OPENINGS = [
    ("B90", "Sicilian Defense, Najdorf Variation",
     "1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6"),
    ("C65", "Ruy Lopez, Berlin Defense", "1.e4 e5 2.Nf3 Nc6 3.Bb5 Nf6"),
    ("D37", "Queen's Gambit Declined", "1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Nf3"),
    ("E60", "King's Indian Defense", "1.d4 Nf6 2.c4 g6 3.Nf3 Bg7"),
    ("C42", "Petrov Defense", "1.e4 e5 2.Nf3 Nf6"),
    ("B12", "Caro-Kann Defense, Advance", "1.e4 c6 2.d4 d5 3.e5"),
    ("A45", "Trompowsky Attack", "1.d4 Nf6 2.Bg5"),
    ("C67", "Ruy Lopez, Open Berlin", "1.e4 e5 2.Nf3 Nc6 3.Bb5 Nf6 4.O-O Nxe4"),
    ("D85", "Grunfeld Defense", "1.d4 Nf6 2.c4 g6 3.Nc3 d5"),
    ("B33", "Sicilian Defense, Sveshnikov", "1.e4 c5 2.Nf3 Nc6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 e5"),
    ("C88", "Ruy Lopez, Closed",
     "1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.O-O Be7 6.Re1 b5 7.Bb3 O-O"),
    ("A04", "Reti Opening", "1.Nf3"),
    ("E20", "Nimzo-Indian Defense", "1.d4 Nf6 2.c4 e6 3.Nc3 Bb4"),
    ("B22", "Sicilian Defense, Alapin", "1.e4 c5 2.c3"),
    ("D02", "London System", "1.d4 d5 2.Nf3 Nf6 3.Bf4"),
    ("C50", "Italian Game", "1.e4 e5 2.Nf3 Nc6 3.Bc4"),
    ("A10", "English Opening", "1.c4"),
    ("B06", "Modern Defense", "1.e4 g6"),
    ("D10", "Slav Defense", "1.d4 d5 2.c4 c6"),
    ("C11", "French Defense, Classical", "1.e4 e6 2.d4 d5 3.Nc3 Nf6"),
]

TOURNAMENT_NAMES = [
    ("Tata Steel 2023", "Wijk aan Zee", "Netherlands"),
    ("Norway Chess", "Stavanger", "Norway"),
    ("Sinquefield Cup", "Saint Louis", "United States"),
    ("Candidates Tournament", "Madrid", "Spain"),
    ("Grand Chess Tour Finals", "London", "United Kingdom"),
    ("FIDE World Cup", "Baku", "Azerbaijan"),
    ("Grenke Chess Classic", "Karlsruhe", "Germany"),
    ("Gashimov Memorial", "Shamkir", "Azerbaijan"),
    ("Aeroflot Open", "Moscow", "Russia"),
    ("Isle of Man Open", "Douglas", "Isle of Man"),
    ("Gibraltar Masters", "Caleta", "Gibraltar"),
    ("Biel Chess Festival", "Biel", "Switzerland"),
    ("Dortmund Sparkassen", "Dortmund", "Germany"),
    ("Legends of Chess", "Bucharest", "Romania"),
    ("Superbet Classic", "Bucharest", "Romania"),
]

# Pool de jugadas SAN plausibles (no se exige legalidad; sí realismo suficiente).
SAN_POOL = [
    "e4", "e5", "d4", "d5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "O-O", "Be7",
    "Re1", "b5", "Bb3", "d6", "c3", "O-O-O", "Bg5", "c5", "cxd4", "Nxd4", "Nc3",
    "g6", "Bg7", "Qd2", "exd5", "Nxd5", "Bd3", "Qe7", "Rfd8", "h3", "Bh5", "g4",
    "Bg6", "Ne5", "Nxg6", "hxg6", "Qf3", "Rad1", "Kh1", "f4", "Rxe7", "Qxf6",
]


def _build_rows(rng: random.Random):
    """Genera todas las filas en memoria respetando las reglas de coherencia."""
    # --- players ---
    players = []
    for i, (name, country, birth, title, peak) in enumerate(REAL_PLAYERS, start=1):
        players.append((i, name, country, birth, title, peak))
    next_id = len(REAL_PLAYERS) + 1
    for _ in range(10):  # 10 sintéticos -> 30 en total
        name = f"{rng.choice(SYNTH_FIRST)} {rng.choice(SYNTH_LAST)}"
        players.append((
            next_id,
            name,
            rng.choice(COUNTRIES),
            rng.randint(1985, 2007),
            rng.choice(TITLES),
            rng.randint(2300, 2650),
        ))
        next_id += 1
    player_ids = [p[0] for p in players]

    # --- openings ---
    openings = [
        (i, eco, name, moves)
        for i, (eco, name, moves) in enumerate(OPENINGS, start=1)
    ]
    opening_ids = [o[0] for o in openings]

    # --- tournaments ---
    tournaments = []
    for i, (name, loc, country) in enumerate(TOURNAMENT_NAMES, start=1):
        # El primer torneo se ancla a 2023 (coincide con su nombre "Tata Steel 2023").
        year = 2023 if i == 1 else rng.randint(2018, 2024)
        start = dt.date(year, rng.randint(1, 11), rng.randint(1, 25))
        end = start + dt.timedelta(days=rng.randint(7, 14))
        tournaments.append((i, name, loc, country, start, end, rng.choice(FORMATS)))

    # --- games + moves ---
    games = []
    moves = []
    move_id = 1
    for game_id in range(1, 151):  # 150 partidas
        tour = rng.choice(tournaments)
        white, black = rng.sample(player_ids, 2)  # jugadores distintos
        opening_id = rng.choice(opening_ids)
        result = rng.choices(RESULTS, weights=[40, 35, 25])[0]
        num_plies = rng.randint(30, 90)  # media jugadas
        game_date = tour[4] + dt.timedelta(days=rng.randint(0, 13))
        rnd = rng.randint(1, 11)
        games.append(
            (game_id, tour[0], white, black, opening_id, result, num_plies, game_date, rnd)
        )
        # moves: una fila por ply; alterna white/black desde el primer movimiento.
        for ply in range(num_plies):
            color = "white" if ply % 2 == 0 else "black"
            move_number = ply // 2 + 1
            moves.append((move_id, game_id, move_number, color, rng.choice(SAN_POOL)))
            move_id += 1

    # --- player_ratings ---
    ratings = []
    rating_id = 1
    peak_by_player = {p[0]: (p[5] or 2500) for p in players}
    for pid in player_ids:
        peak = peak_by_player[pid]
        for year in range(2019, 2025):  # 6 mediciones anuales por jugador
            date = dt.date(year, 6, 1)
            value = max(2200, peak - rng.randint(0, 120))
            ratings.append((rating_id, pid, date, value))
            rating_id += 1

    return players, openings, tournaments, games, moves, ratings


def _apply_schema(cur) -> None:
    cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))


def seed() -> dict[str, int]:
    """Aplica el esquema y carga los datos. Devuelve el conteo por tabla."""
    rng = random.Random(SEED)
    players, openings, tournaments, games, moves, ratings = _build_rows(rng)

    with connect(read_only=False) as conn, conn.cursor() as cur:
        _apply_schema(cur)
        cur.executemany(
            "INSERT INTO players (player_id, name, country, birth_year, title, peak_rating)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            players,
        )
        cur.executemany(
            "INSERT INTO openings (opening_id, eco_code, name, first_moves)"
            " VALUES (%s, %s, %s, %s)",
            openings,
        )
        cur.executemany(
            "INSERT INTO tournaments"
            " (tournament_id, name, location, country, start_date, end_date, format)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s)",
            tournaments,
        )
        cur.executemany(
            "INSERT INTO games (game_id, tournament_id, white_player_id, black_player_id,"
            " opening_id, result, num_moves, date, round)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            games,
        )
        # moves puede ser de miles de filas -> COPY es mucho más rápido que executemany.
        with cur.copy(
            "COPY moves (move_id, game_id, move_number, color, san) FROM STDIN"
        ) as copy:
            for row in moves:
                copy.write_row(row)
        cur.executemany(
            "INSERT INTO player_ratings (rating_id, player_id, rating_date, rating)"
            " VALUES (%s, %s, %s, %s)",
            ratings,
        )
        conn.commit()

    return {
        "players": len(players),
        "openings": len(openings),
        "tournaments": len(tournaments),
        "games": len(games),
        "moves": len(moves),
        "player_ratings": len(ratings),
    }


if __name__ == "__main__":
    counts = seed()
    print("Seed cargado (datos deterministas, semilla fija):")
    for table, n in counts.items():
        print(f"  {table:16s}: {n:>6d} filas")
