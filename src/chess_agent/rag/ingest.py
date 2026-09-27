"""Pipeline de indexado de PDFs para el RAG (T022).

Flujo: PDF -> texto por página (pypdf) -> chunks (~500-800 palabras con solape) -> embeddings
locales -> filas en `document_chunks` (pgvector). Es idempotente por documento: antes de indexar
un PDF borra sus chunks previos, de modo que reemplazar un PDF y volver a correr no duplica datos.

Uso:
    uv run python -m chess_agent.rag.ingest            # indexa todos los PDFs de data/pdfs
    uv run python -m chess_agent.rag.ingest ruta.pdf   # indexa un PDF puntual
"""

from __future__ import annotations

import sys
from pathlib import Path

from pgvector.psycopg import register_vector
from pypdf import PdfReader

from chess_agent.db.client import connect
from chess_agent.rag.embeddings import embed_texts

PDF_DIR = Path(__file__).resolve().parents[3] / "data" / "pdfs"

# 250 palabras es el balance entre dos problemas opuestos:
# - chunks muy chicos (ej. 50 palabras): el embedding es preciso pero le falta contexto para responder.
# - chunks muy grandes (ej. 600+ palabras): tiene contexto pero el embedding promedia muchos temas
#   y la búsqueda por similitud pierde precisión.
# En documentos de referencia densos (ej. las Leyes FIDE, con muchos artículos cortos por página),
# 250 palabras aíslan cada regla en su propio chunk; con 600 una página entera caía en un solo
# chunk y el embedding promediaba artículos distintos, enterrando la regla buscada.
CHUNK_WORDS = 250
# El solapamiento evita cortar ideas a la mitad: si una regla empieza al final de un chunk
# y termina al principio del siguiente, ambos chunks la contienen completa.
# chunk 1: [palabras 1..250], chunk 2: [palabras 201..450], chunk 3: [palabras 401..650]
OVERLAP_WORDS = 50

# DDL idempotente (espeja la sección RAG de db/schema.sql) para que la ingesta no dependa
# de reejecutar el schema completo (que borraría los datos de dominio).
_VECTOR_DDL = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source    TEXT        NOT NULL,
    page      INTEGER,
    content   TEXT        NOT NULL,
    embedding vector(384) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
    ON document_chunks USING hnsw (embedding vector_cosine_ops);
"""


def _chunk_page(text: str) -> list[str]:
    """Divide el texto de una página en chunks de ~CHUNK_WORDS con solape."""
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = CHUNK_WORDS - OVERLAP_WORDS
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + CHUNK_WORDS])
        if chunk.strip():
            chunks.append(chunk)
        if start + CHUNK_WORDS >= len(words):
            break
    return chunks


def _extract_chunks(pdf_path: Path) -> list[tuple[int, str]]:
    """Devuelve (nro_pagina, texto_chunk) para todo el PDF (páginas desde 1)."""
    reader = PdfReader(str(pdf_path))
    out: list[tuple[int, str]] = []
    for page_num, page in enumerate(reader.pages, start=1):
        for chunk in _chunk_page(page.extract_text() or ""):
            out.append((page_num, chunk))
    return out


def ingest_pdf(pdf_path: Path) -> int:
    """Indexa un PDF. Devuelve la cantidad de chunks insertados."""
    source = pdf_path.name
    pairs = _extract_chunks(pdf_path)
    if not pairs:
        return 0

    embeddings = embed_texts([text for _, text in pairs])
    rows = [
        (source, page, text, embeddings[i])
        for i, (page, text) in enumerate(pairs)
    ]

    with connect(read_only=False) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(_VECTOR_DDL)
            cur.execute("DELETE FROM document_chunks WHERE source = %s", (source,))
            cur.executemany(
                "INSERT INTO document_chunks (source, page, content, embedding)"
                " VALUES (%s, %s, %s, %s)",
                rows,
            )
        conn.commit()
    return len(rows)


def ingest_dir(pdf_dir: Path = PDF_DIR) -> dict[str, int]:
    """Indexa todos los PDFs de un directorio. Devuelve chunks por archivo."""
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(
            f"No hay PDFs en {pdf_dir}. Colocá los documentos de referencia y reintentá."
        )
    return {pdf.name: ingest_pdf(pdf) for pdf in pdfs}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        counts = {Path(sys.argv[1]).name: ingest_pdf(Path(sys.argv[1]))}
    else:
        counts = ingest_dir()
    print("Ingesta RAG completada:")
    for name, n in counts.items():
        print(f"  {name}: {n} chunks")
