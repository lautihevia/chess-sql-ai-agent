# chess-sql-ai-agent

Agente de IA que responde preguntas en lenguaje natural (español o inglés) sobre **partidas de
ajedrez**, decidiendo solo de qué fuente obtener el contexto (**routing**):

- **Base de datos relacional (SQL)** → traduce la pregunta a SQL de solo lectura y la ejecuta.
- **RAG sobre PDFs** → recupera contexto de documentos (Leyes FIDE, teoría de aperturas) y cita la fuente.
- **Ambas** → combina un dato estructurado con conocimiento textual en una sola respuesta.

Trabajo Práctico Integrador — AI Engineering (Ingeniería en Informática, 5.º año).

## Stack

Python 3.13 · Claude API (Haiku) · LangGraph · Supabase (PostgreSQL + pgvector) ·
sentence-transformers (embeddings locales) · Streamlit · LangSmith · GitHub Spec Kit (SDD).

## Arquitectura del agente

Grafo LangGraph con router explícito:

```
pregunta ─► router ─┬─ SQL   ─► sql_node ───────────────► síntesis ─► respuesta
                    ├─ RAG   ─► rag_node ───────────────► síntesis ─► respuesta
                    └─ AMBAS ─► sql_node ─► rag_node ────► síntesis ─► respuesta
```

- **router**: clasifica la pregunta (SQL / RAG / AMBAS) y detecta el idioma.
- **sql_node**: genera SQL → **valida** (solo `SELECT` + `LIMIT`) → ejecuta (conexión de solo
  lectura) → 1 reintento con el error.
- **rag_node**: embebe la pregunta y recupera los top-k fragmentos por similitud en pgvector.
- **síntesis**: redacta la respuesta **solo con la evidencia** (grounding); si no hay, rehúsa.

Diseño detallado en [`docs/`](docs/) y artefactos de SDD en [`specs/001-sql-rag-agent/`](specs/001-sql-rag-agent/).

## Para evaluadores (puesta en marcha)

> Las **credenciales no están en el repositorio** (por seguridad, el archivo `.env` está en
> `.gitignore`). Se comparten **por separado**: recibirás un archivo `.env` ya completo por otro
> medio (correo/mensaje). El proceso es:

1. Cloná el repo e instalá dependencias:
   ```bash
   git clone <repo> && cd chess-sql-ai-agent
   uv sync --extra dev
   ```
2. **Colocá el archivo `.env`** que te compartí en la raíz del proyecto (misma carpeta que este
   README). Ya trae todas las claves cargadas; no hay que editar nada.
3. Los datos ya están cargados en la nube (Supabase): la base y los embeddings persisten, así que
   **no hace falta correr el seed ni la ingesta** para probar. Solo levantá la app:
   ```bash
   uv run streamlit run src/app.py
   ```
4. Se abre en `http://localhost:8501`. Probá los ejemplos del panel lateral o escribí tu pregunta.

> Si preferís reconstruir los datos desde cero (opcional), seguí la sección
> [Preparación de los datos](#preparación-de-los-datos).

## Requisitos

- [Python 3.13](https://www.python.org/) y [uv](https://docs.astral.sh/uv/).
- Cuenta de [Supabase](https://supabase.com/) (proyecto PostgreSQL con extensión `pgvector`).
- API key de [Anthropic](https://console.anthropic.com/) (Claude) y de [LangSmith](https://smith.langchain.com/).
- 2 PDFs de referencia (Leyes FIDE + un texto de teoría de aperturas) en `data/pdfs/`.

## Instalación

```bash
git clone <repo> && cd chess-sql-ai-agent
uv sync --extra dev        # instala dependencias (incluye herramientas de test)
```

## Configuración

Copiá `.env.example` a `.env` y completá los valores:

```bash
cp .env.example .env
```

| Variable | Descripción |
|---|---|
| `ANTHROPIC_API_KEY` | Clave de la API de Claude |
| `ANTHROPIC_MODEL` | Modelo (por defecto `claude-haiku-4-5`) |
| `SUPABASE_DB_URL` | Cadena de conexión Postgres. **Usar el Session Pooler** (IPv4): `postgresql://postgres.<ref>:<pwd>@aws-0-<region>.pooler.supabase.com:5432/postgres` |
| `SUPABASE_URL` / `SUPABASE_KEY` | URL y key del proyecto Supabase |
| `LANGSMITH_API_KEY` | Clave de LangSmith (observabilidad) |
| `LANGSMITH_TRACING` | `true` para trazar en LangSmith |
| `LANGSMITH_PROJECT` | Nombre del proyecto en LangSmith |

> La conexión directa `db.<ref>.supabase.co:5432` es IPv6-only en el free tier; por eso se usa el pooler.

## Preparación de los datos

```bash
# 1. Crea el esquema (6 tablas + pgvector) y carga datos sintéticos deterministas
uv run python -m chess_agent.db.seed

# 2. Indexa los PDFs de data/pdfs/ (chunks + embeddings en pgvector)
uv run python -m chess_agent.rag.ingest
```

Ambos comandos son idempotentes. El seed usa semilla fija (reproducible). La ingesta reemplaza
los chunks por archivo; para reemplazar todos los PDFs conviene vaciar antes `document_chunks`.

## Ejecución

```bash
uv run streamlit run src/app.py
```

Se abre en `http://localhost:8501`. Ejemplos de preguntas:

- Datos (SQL): *"¿cuántas partidas ganó Carlsen con blancas?"*, *"top 5 jugadores por rating"*.
- Reglas/teoría (RAG): *"¿qué establece la regla de la pieza tocada?"*, *"¿cuál es la idea de la Siciliana?"*.
- Mixta: *"¿cuántas veces se jugó la Siciliana y cuál es su idea principal?"*.
- Inglés: *"how many games did Carlsen win with white?"*.

## Pruebas

```bash
uv run pytest tests/unit          # unitarios (validador, seguridad) — sin API
uv run pytest tests/bdd           # escenarios Gherkin end-to-end — requiere API + datos
uv run ruff check src tests       # linting
```

## Evaluación

```bash
uv run python -m tests.eval.run_eval          # métricas + experimento en LangSmith
uv run python -m tests.eval.run_eval --local  # solo métricas locales
```

Mide exactitud de enrutamiento, exactitud SQL, fidelidad RAG (con cita) y tasa de rehúso correcto.

## Estructura

```
src/chess_agent/
├── config.py            # carga de .env + LangSmith
├── state.py             # estado compartido del grafo
├── graph.py             # grafo LangGraph (router → SQL/RAG → síntesis)
├── nodes/               # router, sql_node, rag_node, synthesis
├── sql/                 # generator (text-to-SQL) + validator (guardrails)
├── rag/                 # embeddings, ingest, retriever
└── db/                  # schema.sql, seed.py, client.py (solo lectura)
src/app.py               # interfaz Streamlit
tests/                   # unit, bdd, eval
data/pdfs/               # PDFs de referencia (RAG)
```

## Seguridad (solo lectura)

Dos capas de defensa: el **validador** rechaza todo lo que no sea un único `SELECT` (bloquea
`INSERT/UPDATE/DELETE/DROP/…`, múltiples sentencias e inyecciones) y la **conexión** a la BD es
de solo lectura. Ver `tests/unit/test_security.py`.

## Licencia

MIT.
