# Stack tecnológico

Tecnologías elegidas y **por qué**. Las decisiones con alternativas evaluadas están
registradas como ADRs en [`../decisions/`](../decisions/).

| Capa | Tecnología | Por qué | ADR |
|---|---|---|---|
| Lenguaje | **Python 3.13** | Ecosistema estándar de AI engineering; toda la stack vive acá | — |
| LLM | **Claude API** (Anthropic) | Razonamiento del agente vía API key; modelo económico para routing/SQL | — |
| Embeddings | **sentence-transformers** (multilingüe) | Gratuito, local, sin otra API key; soporta preguntas en español | [0004](../decisions/0004-embeddings-locales.md) |
| Base de datos | **PostgreSQL en Supabase** | Postgres administrado en la nube (free tier), con editor visual | [0002](../decisions/0002-supabase.md) |
| Vector store | **pgvector** (en Supabase) | Unifica datos y vectores en una sola BD en la nube | [0005](../decisions/0005-pgvector.md) |
| Orquestación | **LangGraph** | Grafo explícito para el routing SQL/RAG; control y trazabilidad | [0001](../decisions/0001-langgraph.md) |
| Interfaz | **Streamlit** | UI web en Python puro, sin frontend separado; deploy gratis | — |
| Observabilidad | **LangSmith** | Trazas y evaluación del agente | — |
| Despliegue | **Streamlit Community Cloud** | Hosting gratuito de la app; se conecta a Supabase | — |
| SDD | **GitHub Spec Kit** | Metodología y artefactos (constitution/spec/plan/tasks) | — |
| Testing | **pytest** + **pytest-bdd** | Unit por nodo + escenarios Gherkin ejecutables | — |

## Criterios de promoción cubiertos

Este stack cubre los **5** criterios opcionales del enunciado: nube (Supabase + Streamlit
Cloud), interfaz gráfica (Streamlit), framework agéntico (LangGraph), observabilidad
(LangSmith) y SDD (Spec Kit). Detalle en el README y en el informe.

## Dependencias principales (previstas)

`langgraph`, `langchain-anthropic`, `anthropic`, `langsmith`, `streamlit`,
`sentence-transformers`, `psycopg[binary]` / `sqlalchemy`, `pgvector`, `pypdf`,
`pytest`, `pytest-bdd`. La lista definitiva se fija al implementar (gestión con `uv`).
