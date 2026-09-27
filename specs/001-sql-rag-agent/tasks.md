---
description: "Lista de tareas de implementación"
---

# Tareas: Agente de ajedrez con SQL + RAG

**Entrada**: Documentos de diseño en `/specs/001-sql-rag-agent/`

**Prerrequisitos**: plan.md, spec.md, research.md, data-model.md, contracts/

**Pruebas**: SÍ incluidas — la constitución exige test-first (Principio III) y ya hay escenarios
Gherkin en `docs/requirements/use-cases/`.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Historia]**: a qué historia de usuario pertenece (US1, US2, US3)
- Se incluyen rutas de archivo exactas

## Convenciones de rutas

Proyecto único: `src/`, `tests/` en la raíz del repositorio (ver plan.md).

---

## Fase 1: Setup (infraestructura compartida)

**Propósito**: inicializar el proyecto y su estructura.

- [ ] T001 Crear la estructura de carpetas del proyecto (`src/chess_agent/{nodes,sql,rag,db}`, `tests/{unit,bdd,eval}`, `data/pdfs`) según plan.md
- [ ] T002 Inicializar el proyecto Python con `uv` y declarar dependencias (langgraph, anthropic/langchain-anthropic, langsmith, streamlit, sentence-transformers, psycopg, pgvector, pypdf, pytest, pytest-bdd) en `pyproject.toml`
- [ ] T003 [P] Configurar linting/formato (ruff) en `pyproject.toml`
- [ ] T004 [P] Implementar carga de configuración/secrets desde `.env` en `src/chess_agent/config.py`

---

## Fase 2: Fundacional (prerrequisitos bloqueantes)

**Propósito**: infraestructura central que DEBE estar lista antes de cualquier historia.

**⚠️ CRÍTICO**: ninguna historia de usuario puede empezar hasta terminar esta fase.

- [ ] T005 Crear el esquema de la BD (6 tablas + índice en `moves.game_id`) en `src/chess_agent/db/schema.sql` según data-model.md
- [ ] T006 Implementar cliente de BD de **solo lectura** a Supabase en `src/chess_agent/db/client.py`
- [ ] T007 Implementar el seed de datos sintéticos con semilla fija en `src/chess_agent/db/seed.py` (≥15 registros por tabla; `result` ∈ {`1-0`,`0-1`,`1/2-1/2`}, `color` ∈ {`white`,`black`})
- [ ] T008 Definir el estado compartido del grafo en `src/chess_agent/state.py`
- [ ] T009 Implementar el esqueleto del grafo LangGraph (nodos vacíos + cableado router→…→síntesis) en `src/chess_agent/graph.py`
- [ ] T010 [P] Configurar el trazado con LangSmith (variables y wrapping) en `src/chess_agent/config.py`

**Checkpoint**: fundación lista — pueden comenzar las historias de usuario.

---

## Fase 3: Historia de usuario 1 — Consultas de datos (SQL) (Prioridad: P1) 🎯 MVP

**Objetivo**: responder preguntas de datos traduciéndolas a SQL de solo lectura.

**Prueba independiente**: preguntar "¿cuántas partidas ganó Carlsen con blancas?" y verificar el conteo.

### Pruebas de la Historia 1 ⚠️ (escribir primero, deben fallar antes de implementar)

- [ ] T011 [P] [US1] Cablear los escenarios de `docs/requirements/use-cases/sql-queries.feature` con pytest-bdd en `tests/bdd/test_sql_queries.py`
- [ ] T012 [P] [US1] Test unitario del validador SQL en `tests/unit/test_validator.py` (rechaza `INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE` y múltiples sentencias; agrega `LIMIT`)

### Implementación de la Historia 1

- [ ] T013 [P] [US1] Implementar el validador SQL (solo un `SELECT`; agregar `LIMIT` si falta) en `src/chess_agent/sql/validator.py`
- [ ] T014 [US1] Implementar el generador text-to-SQL en `src/chess_agent/sql/generator.py` usando el esquema (data-dictionary), los ejemplos de `docs/agent/golden-queries.md` y `docs/data/term-mapping.md`
- [ ] T015 [US1] Implementar el nodo SQL (generar → validar → ejecutar → 1 reintento con el error) en `src/chess_agent/nodes/sql_node.py`
- [ ] T016 [US1] Implementar el nodo Router (al menos detección de ruta SQL) en `src/chess_agent/nodes/router.py` según `docs/agent/prompts/router.md`
- [ ] T017 [US1] Implementar el nodo Síntesis con política de grounding en `src/chess_agent/nodes/synthesis.py` según `docs/agent/grounding-policy.md`
- [ ] T018 [US1] Interfaz Streamlit mínima (input de pregunta + respuesta + SQL generado) en `src/app.py`

**Checkpoint**: US1 funcional y testeable de forma independiente (MVP).

---

## Fase 4: Historia de usuario 2 — Consultas de reglas/teoría (RAG) (Prioridad: P2)

**Objetivo**: responder preguntas conceptuales con RAG sobre los PDFs, citando la fuente.

**Prueba independiente**: preguntar por una regla FIDE y verificar respuesta correcta con cita.

### Pruebas de la Historia 2 ⚠️

- [ ] T019 [P] [US2] Cablear `docs/requirements/use-cases/rag-queries.feature` con pytest-bdd en `tests/bdd/test_rag_queries.py`

### Implementación de la Historia 2

- [ ] T020 [P] [US2] Implementar embeddings locales multilingües en `src/chess_agent/rag/embeddings.py`
- [ ] T021 [US2] Habilitar `pgvector` y crear la tabla de vectores (extender `src/chess_agent/db/schema.sql`)
- [ ] T022 [US2] Implementar el pipeline de indexado (PDF → chunks ~500-800 palabras con solape → embeddings → pgvector) en `src/chess_agent/rag/ingest.py`
- [ ] T023 [US2] Implementar el recuperador (top-k=4, umbral; devuelve fragmentos + fuente/página) en `src/chess_agent/rag/retriever.py`
- [ ] T024 [US2] Implementar el nodo RAG (recupera → contexto; si vacío, rehúsa) en `src/chess_agent/nodes/rag_node.py` según `docs/agent/prompts/rag.md`
- [ ] T025 [US2] Extender el nodo Síntesis para citar la fuente en respuestas RAG en `src/chess_agent/nodes/synthesis.py`
- [ ] T026 [US2] Extender la UI para mostrar las fuentes citadas en `src/app.py`

**Checkpoint**: US1 y US2 funcionan de forma independiente.

---

## Fase 5: Historia de usuario 3 — Enrutamiento, mixtas y multilingüe (Prioridad: P3)

**Objetivo**: decidir la fuente automáticamente, combinar ambas y soportar español/inglés.

**Prueba independiente**: preguntas puras de datos, puras conceptuales, mixtas y en inglés.

### Pruebas de la Historia 3 ⚠️

- [ ] T027 [P] [US3] Cablear `docs/requirements/use-cases/routing.feature` con pytest-bdd en `tests/bdd/test_routing.py`

### Implementación de la Historia 3

- [ ] T028 [US3] Ampliar el router a SQL/RAG/AMBAS + detección de idioma en `src/chess_agent/nodes/router.py`
- [ ] T029 [US3] Implementar la rama AMBAS en el grafo (SQL + RAG → síntesis combinada) en `src/chess_agent/graph.py`
- [ ] T030 [US3] Garantizar que la respuesta salga en el idioma de la pregunta en `src/chess_agent/nodes/synthesis.py`

**Checkpoint**: las tres historias funcionan de forma independiente.

---

## Fase 6: Pulido y aspectos transversales

**Propósito**: calidad, evaluación, seguridad, despliegue e informe.

- [ ] T031 [P] Construir el dataset de evaluación (golden-queries + RAG + casos de rehúso, es/en) en `tests/eval/dataset.py`
- [ ] T032 Ejecutar el experimento de evaluación en LangSmith y registrar métricas (según `docs/quality/evaluation.md`)
- [ ] T033 [P] Test de seguridad: intentos de inyección de prompt y de escritura en `tests/unit/test_security.py`
- [ ] T034 [P] Escribir el `README.md` con instrucciones de instalación y ejecución
- [ ] T035 Desplegar en Supabase + Streamlit Community Cloud y configurar los secrets (según `docs/architecture/deployment.md`)
- [ ] T036 Ejecutar la validación de `quickstart.md` (5 escenarios) y capturar evidencias
- [ ] T037 [P] Completar el informe técnico (≤10 pág) siguiendo `docs/informe-outline.md`

---

## Dependencias y orden de ejecución

- **Setup (Fase 1)**: sin dependencias.
- **Fundacional (Fase 2)**: depende del Setup; **bloquea** todas las historias.
- **Historias (Fases 3-5)**: dependen de la Fase 2. En prioridad P1 → P2 → P3 (al ser individual, secuencial).
- **Pulido (Fase 6)**: depende de las historias deseadas terminadas.

### Dentro de cada historia
- Los tests se escriben y **deben fallar** antes de implementar.
- SQL: validador antes que generador antes que nodo.
- RAG: embeddings/ingesta antes que recuperador antes que nodo.

### Oportunidades de paralelismo
- T003/T004 en paralelo (Setup).
- Tests marcados [P] de cada historia en paralelo con otros archivos distintos.

---

## Estrategia de implementación

### MVP primero (solo US1)
1. Fase 1 (Setup) → 2. Fase 2 (Fundacional) → 3. Fase 3 (US1) → **validar** → demo.

### Entrega incremental
Setup + Fundacional → US1 (MVP) → US2 → US3 → Pulido. Cada historia agrega valor sin romper la anterior.

---

## Notas

- [P] = archivos distintos, sin dependencias.
- Commit después de cada tarea o grupo lógico (mensajes en inglés, sin co-author).
- Verificar que los tests fallan antes de implementar.
- Cada historia se valida de forma independiente en su checkpoint.

## Resumen

- **Total de tareas**: 37 (T001–T037)
- **Por fase**: Setup 4 · Fundacional 6 · US1 8 · US2 8 · US3 4 · Pulido 7
- **MVP sugerido**: Fases 1-3 (hasta T018) → agente de datos (SQL) funcionando end-to-end.
