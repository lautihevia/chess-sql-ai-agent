"""Embeddings locales multilingües (T020).

Usa `sentence-transformers` (ADR 0004): sin costo de API y con soporte de español e inglés,
para que las preguntas en español recuperen bien sobre documentos que pueden estar en inglés.
Los vectores se normalizan (norma 1) para que la distancia coseno de pgvector sea consistente.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

# Modelo multilingüe liviano (384 dimensiones). Candidato de research.md.
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

#Este archivo tiene como objetivo convertir el texto en un vector numerico osea un embedding. Ese modelo que esta arriba
#es un modelo local que se descarga una sola vez y corre de manera local.
@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    """Carga el modelo una sola vez (se descarga en la primera ejecución)."""
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Devuelve una matriz (n, 384) de embeddings normalizados."""
    return _model().encode(
        list(texts), normalize_embeddings=True, convert_to_numpy=True
    )


def embed_query(text: str) -> np.ndarray:
    """Embedding (384,) de una única consulta."""
    return embed_texts([text])[0]
