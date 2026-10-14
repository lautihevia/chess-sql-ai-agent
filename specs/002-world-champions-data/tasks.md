---
description: "Lista de tareas de implementación"
---

# Tareas: Datos de campeonatos mundiales de ajedrez

**Entrada**: Documentos de diseño en `/specs/002-world-champions-data/`

**Prerrequisitos**: plan.md, spec.md, research.md, data-model.md

**Nota**: lista retroactiva. Las tareas marcadas `[x]` ya están implementadas y verificadas en la
PR #1; las desmarcadas son trabajo abierto.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: puede ejecutarse en paralelo
- **[Historia]**: US1 (datos), US2 (historia narrada), US3 (rechazo honesto)

---

## Fase 1: Documentos (RAG)

- [x] T001 [P] [US2] Descargar y agregar `list-of-world-chess-championships.pdf` y `world-chess-championship.pdf` a `data/pdfs/`
- [x] T002 [P] [US2] Agregar `campeonato-mundial-de-ajedrez.pdf` (versión en español) a `data/pdfs/`
- [x] T003 [US2] Indexar los PDFs en Supabase (`uv run python -m chess_agent.rag.ingest`)

## Fase 2: Datos SQL

- [x] T004 [US1] Crear las tablas `champions` y `world_championships` en `src/chess_agent/db/schema.sql`
- [x] T005 [US1] Cargar los 58 campeonatos desde el PDF en `src/chess_agent/db/championships.py`
- [x] T006 [US1] Cargar las 44 personas con años de nacimiento y muerte (Wikidata) en `championships.py`
- [x] T007 [US1] Vincular `champions` con `players` por FIDE ID (`players.fide_id`), verificando los ids contra ratings.fide.com
- [x] T008 [US1] Cargar las tablas al regenerar la base (`src/chess_agent/db/seed.py`) y de forma independiente (`python -m chess_agent.db.championships`)
- [x] T009 [P] [US1] Pruebas unitarias de integridad de los datos en `tests/unit/test_championships.py`

## Fase 3: Agente

- [x] T010 [US1] Router: datos de campeones → SQL; historia y récords → RAG (`src/chess_agent/nodes/router.py`)
- [x] T011 [US1] Generador SQL: ejemplos few-shot con JOIN, reglas de mapeo y `NO_SQL` para reinados (`src/chess_agent/sql/generator.py`)
- [x] T012 [P] [US1] Agregar 4 casos al dataset de evaluación (`tests/eval/dataset.py`)

## Fase 4: Corrección del RAG

- [x] T013 [US2] Medir qué porcentaje de chunks supera la ventana de 128 tokens del modelo de embeddings
- [x] T014 [US2] Cambiar `CHUNK_WORDS` a 70, `OVERLAP_WORDS` a 15 y `DEFAULT_K` a 8; reindexar
- [x] T015 [US2] Documentar la decisión y las alternativas en `docs/decisions/0006-tamano-de-chunk-y-k.md`

## Fase 5: Documentación

- [x] T016 [P] Actualizar README, diccionario de datos, modelo de datos, mapeo de términos, consultas de referencia, prompt del router, informe y preguntas abiertas
- [x] T017 [P] Crear esta spec (`specs/002-world-champions-data/`)

## Fase 6: Pendiente / mejoras

- [ ] T018 Traducir la pregunta al inglés antes de recuperar, para mejorar el RAG en español ("rey ahogado", "PCA")
- [ ] T019 Reemplazar o quitar del dataset de evaluación los dos casos de la Defensa Siciliana (el contenido no está en los documentos indexados)
- [ ] T020 Evaluar completar `champions` con país y duración de reinados a partir de la tabla del PDF en español (página 10)
- [ ] T021 Feature aparte: cargar partidas reales desde archivos PGN (pregunta Q5 de `docs/open-questions.md`)

## Dependencias

- T004 → T005, T006 → T007 → T008.
- T010 y T011 dependen de que las tablas existan (T004–T008).
- T013 → T014 → T015.
