-- Esquema de la BD de ajedrez (8 tablas relacionales).
-- Fuente de verdad: docs/data/data-dictionary.md y specs/001-sql-rag-agent/data-model.md.
--
-- Los IDs son enteros asignados explícitamente por el seed (no SERIAL) para que la generación
-- de datos sea determinista y reproducible (semilla fija, Principio V).
-- Re-ejecutable: elimina las tablas en orden inverso a sus dependencias antes de crearlas.

DROP TABLE IF EXISTS world_championships CASCADE;
DROP TABLE IF EXISTS champions CASCADE;
DROP TABLE IF EXISTS player_ratings CASCADE;
DROP TABLE IF EXISTS moves CASCADE;
DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS tournaments CASCADE;
DROP TABLE IF EXISTS openings CASCADE;
DROP TABLE IF EXISTS players CASCADE;

-- ---------------------------------------------------------------------------
-- players — jugadores
-- ---------------------------------------------------------------------------
CREATE TABLE players (
    player_id   INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    country     TEXT,
    birth_year  INTEGER,
    title       TEXT    CHECK (title IN ('GM', 'IM', 'FM', 'WGM', 'WIM', 'CM', 'NM')),
    peak_rating INTEGER,
    -- FIDE ID (ej. 1503014 = Magnus Carlsen): identifica a la persona real sin depender de cómo
    -- se escribe el nombre. NULL en los jugadores sintéticos. Une players con champions.
    fide_id     INTEGER UNIQUE
);

-- ---------------------------------------------------------------------------
-- openings — aperturas (catálogo ECO)
-- ---------------------------------------------------------------------------
CREATE TABLE openings (
    opening_id  INTEGER PRIMARY KEY,
    eco_code    TEXT    NOT NULL,
    name        TEXT    NOT NULL,
    first_moves TEXT
);

-- ---------------------------------------------------------------------------
-- tournaments — torneos
-- ---------------------------------------------------------------------------
CREATE TABLE tournaments (
    tournament_id INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    location      TEXT,
    country       TEXT,
    start_date    DATE,
    end_date      DATE,
    format        TEXT    CHECK (format IN ('round-robin', 'swiss', 'knockout'))
);

-- ---------------------------------------------------------------------------
-- games — partidas (tabla central)
-- ---------------------------------------------------------------------------
CREATE TABLE games (
    game_id         INTEGER PRIMARY KEY,
    tournament_id   INTEGER REFERENCES tournaments (tournament_id),
    white_player_id INTEGER NOT NULL REFERENCES players (player_id),
    black_player_id INTEGER NOT NULL REFERENCES players (player_id),
    opening_id      INTEGER REFERENCES openings (opening_id),
    result          TEXT    NOT NULL CHECK (result IN ('1-0', '0-1', '1/2-1/2')),
    num_moves       INTEGER,
    date            DATE,
    round           INTEGER,
    -- Blancas y negras de una misma partida son jugadores distintos.
    CONSTRAINT chk_distinct_players CHECK (white_player_id <> black_player_id)
);

-- ---------------------------------------------------------------------------
-- moves — jugadas (una fila por media jugada / ply)
-- ---------------------------------------------------------------------------
CREATE TABLE moves (
    move_id     INTEGER PRIMARY KEY,
    game_id     INTEGER NOT NULL REFERENCES games (game_id),
    move_number INTEGER NOT NULL,
    color       TEXT    NOT NULL CHECK (color IN ('white', 'black')),
    san         TEXT    NOT NULL
);

-- Índice para reconstruir partidas de forma eficiente (ADR 0003).
CREATE INDEX idx_moves_game_id ON moves (game_id);

-- ---------------------------------------------------------------------------
-- player_ratings — historial de rating
-- ---------------------------------------------------------------------------
CREATE TABLE player_ratings (
    rating_id   INTEGER PRIMARY KEY,
    player_id   INTEGER NOT NULL REFERENCES players (player_id),
    rating_date DATE    NOT NULL,
    rating      INTEGER NOT NULL
);

-- Índices de apoyo para consultas frecuentes (rankings, filtros por jugador).
CREATE INDEX idx_games_white_player ON games (white_player_id);
CREATE INDEX idx_games_black_player ON games (black_player_id);
CREATE INDEX idx_player_ratings_player ON player_ratings (player_id);

-- ---------------------------------------------------------------------------
-- champions — personas que jugaron un campeonato mundial (datos reales, de Wikidata)
-- birth_year / death_year: de Wikidata; death_year NULL = vivo. fide_id: FIDE ID verificado contra
-- ratings.fide.com; NULL en los campeones históricos anteriores al sistema de ratings.
-- player_id: vínculo OPCIONAL con players, por fide_id (hoy 8 de 44); el resto queda en
-- NULL en lugar de inventar jugadores sintéticos para los campeones históricos.
-- ---------------------------------------------------------------------------
CREATE TABLE champions (
    champion_id INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL UNIQUE,
    birth_year  INTEGER NOT NULL,
    death_year  INTEGER,
    fide_id     INTEGER UNIQUE,
    player_id   INTEGER REFERENCES players (player_id)
);

-- ---------------------------------------------------------------------------
-- world_championships — historial de campeonatos mundiales (datos reales, 1886-2024)
-- Fuente: data/pdfs/list-of-world-chess-championships.pdf. Se carga con seed.py o, sola, con
-- db/championships.py (recrea champions y world_championships sin tocar las demás tablas).
-- title_line: 'main' = linaje principal (privado hasta 1946, FIDE desde 1948, reunificado
--             desde 2006); 'classical' = título clásico PCA 1993-2004; 'fide_split' = título
--             FIDE durante el cisma 1993-2005. Hay varias filas en 1993 y en 2000/2004.
-- ---------------------------------------------------------------------------
CREATE TABLE world_championships (
    championship_id INTEGER PRIMARY KEY,
    year            INTEGER NOT NULL,   -- año en que se jugó (si cruza año, el de inicio)
    location        TEXT,               -- sede (ciudades, en inglés)
    winner_id       INTEGER NOT NULL REFERENCES champions (champion_id),  -- ganó o retuvo
    win_number      INTEGER NOT NULL,   -- n-ésimo título de ese jugador (como numera la fuente)
    runner_up_id    INTEGER NOT NULL REFERENCES champions (champion_id),  -- rival
    score           TEXT,               -- marcador, ganador primero (NULL si no hubo match)
    title_line      TEXT    NOT NULL CHECK (title_line IN ('main', 'classical', 'fide_split')),
    format          TEXT    NOT NULL CHECK (format IN ('match', 'tournament', 'knockout'))
);

-- ---------------------------------------------------------------------------
-- RAG: vectores de los fragmentos de PDFs (pgvector).
-- No se elimina al reseed de datos de dominio: usa IF NOT EXISTS y vive aparte.
-- La ingesta (rag/ingest.py) también garantiza esta estructura de forma idempotente.
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source    TEXT        NOT NULL,   -- nombre del PDF de origen
    page      INTEGER,                -- página para citar la fuente
    content   TEXT        NOT NULL,   -- texto del fragmento
    embedding vector(384) NOT NULL    -- embedding multilingüe (MiniLM-L12)
);

-- Índice HNSW para búsqueda por similitud coseno (pgvector >= 0.5).
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
    ON document_chunks USING hnsw (embedding vector_cosine_ops);
