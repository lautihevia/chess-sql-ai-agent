# Investigación (Fase 0)

Consolidación de decisiones técnicas. Las decisiones formales están registradas como ADRs en
[`docs/decisions/`](../../docs/decisions/); acá se resumen y se resuelven las incógnitas abiertas.

## Decisiones (resumen de ADRs)

| Tema | Decisión | Racional breve | ADR |
|---|---|---|---|
| Orquestación | LangGraph con router explícito | Control, trazabilidad, cumple criterio agéntico | 0001 |
| Base de datos | PostgreSQL en Supabase | Nube gratuita, editor visual, pgvector | 0002 |
| Modelado de jugadas | Una fila por ply, indexada | Consultas a nivel jugada sin costo relevante | 0003 |
| Embeddings | sentence-transformers local (multilingüe) | Gratis, sin API extra, soporta español | 0004 |
| Vector store | pgvector en Supabase (plan B: Chroma) | Todo en una BD en la nube | 0005 |

## Incógnitas resueltas (de open-questions)

### Modelo de Claude por nodo
- **Decisión**: modelo económico para routing y text-to-SQL; modelo de gama media para síntesis.
- **Racional**: routing y SQL son tareas acotadas; la síntesis se beneficia de mejor redacción.
- **Alternativas**: usar un único modelo para todo (más simple pero menos costo-eficiente). Los IDs
  y precios exactos se confirman al implementar (skill `claude-api`).

### PDFs de referencia (RAG)
- **Decisión**: (1) Leyes del Ajedrez de FIDE (reglas) y (2) un texto de teoría de aperturas de
  licencia abierta.
- **Racional**: cubren dos tipos de preguntas conceptuales distintas y no se solapan con el SQL.
- **Alternativas**: usar más PDFs (innecesario; el mínimo son 2).

### Modelo de embeddings multilingüe
- **Decisión**: un modelo multilingüe de `sentence-transformers` (candidatos: `multilingual-e5`,
  `paraphrase-multilingual-MiniLM`).
- **Racional**: preguntas en español, documentos posiblemente en inglés.
- **Alternativas**: modelo solo-inglés (peor para consultas en español).

### Parámetros de chunking y recuperación
- **Decisión**: chunks de ~500–800 palabras con solape; `k` inicial = 4.
- **Racional**: equilibrio entre contexto suficiente y precisión; se ajusta con la evaluación.
- **Alternativas**: chunks muy chicos (pierden contexto) o muy grandes (ruido).

### Origen de los datos de partidas
- **Decisión**: datos sintéticos generados por script con semilla fija.
- **Racional**: cumple el enunciado y garantiza reproducibilidad; suficiente para consultas
  significativas.
- **Alternativas**: dataset real (PGN) — mayor realismo pero más complejidad de ingesta.

**Salida**: todas las incógnitas de [`docs/open-questions.md`](../../docs/open-questions.md) tienen
una decisión de trabajo. Los detalles finos se afinan empíricamente durante la implementación.
