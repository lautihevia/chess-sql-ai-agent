# chess-sql-ai-agent

Agente de IA que responde preguntas en lenguaje natural sobre **partidas de ajedrez**,
combinando dos fuentes y decidiendo solo de cuál obtener el contexto (routing):

- **Base de datos relacional (SQL)** → traduce la pregunta a SQL y la ejecuta.
- **RAG sobre PDFs** → recupera contexto de documentos (Leyes FIDE, teoría de aperturas).

Trabajo Práctico Integrador — AI Engineering (Ingeniería en Informática, 5to año).

> 🚧 En construcción. La documentación de diseño vive en [`docs/`](docs/) y las
> instrucciones de instalación y ejecución se completan a medida que avanza el desarrollo.

## Stack

Python · Claude API · LangGraph · Supabase (Postgres + pgvector) · sentence-transformers ·
Streamlit · LangSmith · GitHub Spec Kit (SDD).
