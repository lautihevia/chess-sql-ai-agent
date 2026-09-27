"""Recuperador de fragmentos por similitud en pgvector (T023).

Embebe la pregunta y busca los top-k fragmentos más cercanos por distancia coseno. Aplica un
umbral de similitud: si ningún fragmento lo supera, devuelve lista vacía (Contrato 3) y el
agente rehúsa en lugar de inventar. Cada fragmento incluye su procedencia (fuente + página).
"""

from __future__ import annotations

from pgvector.psycopg import register_vector

from chess_agent.db.client import STATEMENT_TIMEOUT_MS, connect
from chess_agent.rag.embeddings import embed_query
from chess_agent.state import RagChunk

DEFAULT_K = 4
# Similitud coseno mínima (0-1). Umbral BAJO a propósito: se prioriza el recall (traer los
# fragmentos potencialmente útiles) y se delega la decisión final de grounding al nodo de
# síntesis, que responde NO_ANSWER si el contexto recuperado no cubre la pregunta. El modelo
# MiniLM multilingüe tiene poca separación de scores (relevantes ~0.55-0.74, ruido ~0.35-0.50),
# por lo que un umbral alto descartaría reformulaciones válidas.
DEFAULT_THRESHOLD = 0.45

_SQL = """
SELECT source, page, content, 1 - (embedding <=> %s) AS score
FROM document_chunks
ORDER BY embedding <=> %s
LIMIT %s
"""


def retrieve(
    pregunta: str, k: int = DEFAULT_K, threshold: float = DEFAULT_THRESHOLD
) -> list[RagChunk]:
    """Devuelve hasta `k` fragmentos con similitud >= `threshold` para la pregunta."""
    vec = embed_query(pregunta)
    with connect(read_only=True) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(f"SET statement_timeout = {STATEMENT_TIMEOUT_MS}")
            cur.execute(_SQL, (vec, vec, k))
            rows = cur.fetchall()

    return [
        RagChunk(
            text=row["content"],
            source=row["source"],
            page=row["page"],
            score=float(row["score"]),
        )
        for row in rows
        if row["score"] is not None and float(row["score"]) >= threshold
    ]
