# ADR 0004 — Embeddings locales (sentence-transformers)

- **Estado:** aceptada
- **Fecha:** 2026-09-26

## Contexto

El RAG necesita convertir texto en vectores. Las preguntas van en **español** (y a veces
inglés) y los PDFs pueden estar en inglés, así que el modelo debe ser **multilingüe**.
También se busca minimizar costos y claves de API.

## Decisión

Usar **`sentence-transformers`** con un modelo **multilingüe**, ejecutado **en local**.

## Alternativas consideradas

- **Embeddings por API (ej. OpenAI/Voyage):** buena calidad, pero suma otra API key y costo.
- Anthropic no ofrece endpoint de embeddings propio, por lo que Claude no cubre esta parte.

## Consecuencias

- (+) Gratuito y sin API key adicional.
- (+) Soporta consultas en español.
- (+) Reproducible (el modelo se descarga y corre localmente).
- (−) Consume algo de CPU/memoria local al indexar (volumen chico, aceptable).
