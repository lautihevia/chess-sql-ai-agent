# Plan de implementación: Agente de ajedrez con SQL + RAG

**Rama**: `001-sql-rag-agent` | **Fecha**: 2026-09-27 | **Spec**: [spec.md](spec.md)

**Entrada**: Especificación de `specs/001-sql-rag-agent/spec.md`

## Resumen

Se construye un agente conversacional que responde preguntas en lenguaje natural sobre ajedrez
decidiendo automáticamente la fuente: una **base de datos relacional** (traducción de la pregunta
a SQL) y un **repositorio documental** (RAG sobre PDFs). El enfoque técnico es un grafo de nodos
(router → SQL/RAG → síntesis) orquestado con LangGraph, con Claude como motor de razonamiento,
embeddings locales para el RAG, PostgreSQL + pgvector en Supabase, interfaz Streamlit y
observabilidad con LangSmith. Detalle de arquitectura en [`docs/architecture/`](../../docs/architecture/)
y flujo del agente en [`docs/agent/agent-flow.md`](../../docs/agent/agent-flow.md).

## Contexto técnico

**Lenguaje/Versión**: Python 3.13

**Dependencias principales**: LangGraph, langchain-anthropic / anthropic, langsmith, streamlit,
sentence-transformers, psycopg / SQLAlchemy, pgvector, pypdf, pytest, pytest-bdd

**Almacenamiento**: PostgreSQL en Supabase (datos relacionales) + pgvector (vectores del RAG)

**Pruebas**: pytest (unitarias por nodo) + pytest-bdd (escenarios Gherkin) + evaluación en LangSmith

**Plataforma objetivo**: Local (desarrollo) y Streamlit Community Cloud (despliegue)

**Tipo de proyecto**: Aplicación web con agente de IA (single project, un solo proceso)

**Objetivos de rendimiento**: Respuesta conversacional en un tiempo razonable (objetivo orientativo
< 10 s por consulta)

**Restricciones**: Solo lectura sobre la BD; secretos fuera del repo; costo de API acotado usando
un modelo económico para routing/SQL

**Escala/Alcance**: Datos sintéticos (~6 tablas, cientos–miles de filas), 2 PDFs, uso individual/demo

## Verificación de constitución

*GATE: debe pasar antes de la investigación (Fase 0). Reverificar tras el diseño (Fase 1).*

| Principio | ¿Cumple el plan? |
|---|---|
| I. Grounding-first | ✅ Nodos separados con política de grounding; síntesis solo con evidencia |
| II. Seguridad y solo lectura | ✅ Validador de SQL + rol de BD de solo lectura + secretos en entorno |
| III. Verificabilidad (test-first) | ✅ Gherkin ya escrito; unit por nodo; eval en LangSmith |
| IV. Observabilidad | ✅ LangSmith integrado desde el inicio |
| V. Reproducibilidad y documentación | ✅ Seed determinista + README + ADRs |
| VI. Simplicidad (YAGNI) | ✅ Single project, servicios gratuitos managed, sin capas innecesarias |

**Resultado**: sin violaciones. No se requiere Complexity Tracking.

## Estructura del proyecto

### Documentación (esta funcionalidad)

```text
specs/001-sql-rag-agent/
├── plan.md              # Este archivo
├── research.md          # Fase 0 (decisiones e investigación)
├── data-model.md        # Fase 1 (modelo de datos)
├── quickstart.md        # Fase 1 (guía de validación end-to-end)
├── contracts/           # Fase 1 (contratos de interfaces)
└── tasks.md             # Fase 2 (/speckit-tasks)
```

### Código fuente (raíz del repositorio)

```text
src/
├── chess_agent/
│   ├── config.py            # carga de configuración/secrets
│   ├── state.py             # estado compartido del grafo
│   ├── graph.py             # definición del grafo LangGraph
│   ├── nodes/
│   │   ├── router.py        # clasificación SQL/RAG/AMBAS
│   │   ├── sql_node.py      # text-to-SQL + validación + ejecución
│   │   ├── rag_node.py      # recuperación de contexto
│   │   └── synthesis.py     # redacción final
│   ├── sql/
│   │   ├── generator.py     # generación de SQL (Claude)
│   │   └── validator.py     # guardrails: solo SELECT + LIMIT
│   ├── rag/
│   │   ├── ingest.py        # pipeline de indexado de PDFs
│   │   ├── embeddings.py    # embeddings locales (multilingüe)
│   │   └── retriever.py     # búsqueda por similitud en pgvector
│   └── db/
│       ├── schema.sql       # CREATE TABLE + índices
│       ├── seed.py          # datos sintéticos (semilla fija)
│       └── client.py        # conexión de solo lectura a Supabase
└── app.py                   # interfaz Streamlit

tests/
├── unit/                    # pruebas por nodo/validador
├── bdd/                     # pytest-bdd (usa docs/requirements/use-cases/*.feature)
└── eval/                    # dataset + evaluación LangSmith

data/
└── pdfs/                    # los 2 PDFs de referencia (RAG)
```

**Decisión de estructura**: proyecto único (single project). Un paquete `chess_agent` con
submódulos por responsabilidad (nodos, sql, rag, db) + `app.py` para la UI. Refleja los
componentes de [`docs/architecture/container-view.md`](../../docs/architecture/container-view.md)
y facilita probar cada nodo de forma aislada (Principio III).

## Complexity Tracking

No aplica: la verificación de constitución no arrojó violaciones.
