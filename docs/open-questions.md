# Preguntas abiertas

Documento **vivo**: decisiones o dudas pendientes de resolver. Se actualiza a medida que
avanza el proyecto; al cerrarse, la decisión se mueve a un ADR en [`decisions/`](decisions/).

## Abiertas

| # | Pregunta | Notas | Estado |
|---|---|---|---|
| Q1 | ¿Qué modelo Claude exacto para cada nodo? (routing/SQL vs síntesis) | Definir IDs y costo al implementar; probablemente uno económico para routing/SQL | Abierta |
| Q2 | ¿Qué PDFs concretos para el RAG? | Candidatos: Leyes FIDE (oficial) + un texto de teoría de aperturas de licencia abierta | Abierta |
| Q3 | ¿Modelo de embeddings multilingüe específico? | Candidatos: `paraphrase-multilingual-MiniLM`, `multilingual-e5` | Abierta |
| Q4 | ¿Tamaño de chunk y `k` de recuperación? | Ajustar empíricamente con la evaluación | Abierta |
| Q5 | ¿Se usa un dataset real de partidas (PGN) o 100% sintético? | Sintético alcanza; un dataset real daría más realismo | Abierta |
| Q6 | ¿Mostrar el grafo del agente en la UI? | Suma para el coloquio; opcional | Abierta |

## Resueltas (referencia)

| Pregunta | Decisión | ADR |
|---|---|---|
| ¿Framework de orquestación? | LangGraph | [0001](decisions/0001-langgraph.md) |
| ¿Base de datos? | Supabase (Postgres) | [0002](decisions/0002-supabase.md) |
| ¿Modelado de `moves`? | Una fila por ply, con índice | [0003](decisions/0003-moves-por-ply.md) |
| ¿Embeddings? | Locales (sentence-transformers) | [0004](decisions/0004-embeddings-locales.md) |
| ¿Vector store? | pgvector en Supabase (plan B: Chroma) | [0005](decisions/0005-pgvector.md) |
