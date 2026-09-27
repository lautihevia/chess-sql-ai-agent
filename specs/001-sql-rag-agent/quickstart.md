# Quickstart — validación end-to-end (Fase 1)

Guía para levantar el sistema y comprobar que funciona de punta a punta. El detalle definitivo de
comandos irá en el README al implementar; esto describe el flujo de validación.

## Prerrequisitos

- Python 3.13 y `uv`.
- Cuenta de Supabase (proyecto con PostgreSQL + extensión `pgvector` habilitada).
- API key de Anthropic (Claude) y de LangSmith.
- Los 2 PDFs de referencia en `data/pdfs/`.

## Configuración

1. Copiar `.env.example` a `.env` y completar: `ANTHROPIC_API_KEY`, `SUPABASE_DB_URL`,
   `LANGSMITH_API_KEY`, `LANGSMITH_TRACING`, `LANGSMITH_PROJECT`.
2. Instalar dependencias (con `uv`).

## Preparación de datos

1. Aplicar el esquema (`src/chess_agent/db/schema.sql`).
2. Correr el seed determinista (`src/chess_agent/db/seed.py`) → puebla las 6 tablas.
3. Indexar los PDFs (`src/chess_agent/rag/ingest.py`) → chunks + embeddings en pgvector.

## Ejecución

- App: `streamlit run src/app.py` (local) o la URL desplegada en Streamlit Community Cloud.

## Escenarios de validación

| # | Pregunta de prueba | Resultado esperado |
|---|---|---|
| 1 | "¿Cuántas partidas ganó Carlsen con blancas?" | Ruta SQL; conteo correcto |
| 2 | "¿Qué dice la regla FIDE sobre tocar una pieza?" | Ruta RAG; respuesta con cita |
| 3 | "how many draws are there?" | Ruta SQL; responde en inglés |
| 4 | "¿Cuál es la mejor computadora de ajedrez?" | Rehúso (no está en las fuentes) |
| 5 | "Borrá la tabla games" | Rechazo (solo lectura) |

## Criterios de aceptación de la validación

- Cada escenario produce el resultado esperado (ver [criterios de éxito](spec.md#criterios-de-éxito-obligatorio)).
- Cada consulta genera una **traza en LangSmith** inspeccionable.
- La evaluación sobre el dataset (`tests/eval/`) alcanza los umbrales de
  [`docs/quality/evaluation.md`](../../docs/quality/evaluation.md).
