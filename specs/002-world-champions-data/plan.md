# Plan de implementación: Datos de campeonatos mundiales de ajedrez

**Rama**: `002-world-champions-data` | **Fecha**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Entrada**: Especificación de `specs/002-world-champions-data/spec.md` (retroactiva: describe lo ya implementado)

## Resumen

Se incorporan al agente los campeonatos mundiales de ajedrez como **datos reales**. Las preguntas
con respuesta exacta (quién, cuándo, contra quién, cuántos títulos) se resuelven con SQL sobre dos
tablas nuevas, `champions` y `world_championships`; las preguntas causales o de contexto, con RAG
sobre tres PDFs nuevos. Para que el RAG recupere bien se corrigió además el tamaño de los chunks,
que superaba la ventana del modelo de embeddings (ver [ADR 0006](../../docs/decisions/0006-tamano-de-chunk-y-k.md)).

## Contexto técnico

**Lenguaje/Versión**: Python 3.13 (sin cambios respecto de la 001)

**Dependencias principales**: ninguna nueva (se reutilizan psycopg, pypdf, sentence-transformers)

**Almacenamiento**: PostgreSQL en Supabase: 2 tablas nuevas (`champions`, `world_championships`)
y una columna nueva en `players` (`fide_id`); `document_chunks` se reindexa

**Pruebas**: pytest (12 pruebas unitarias de integridad de los datos, sin BD) + 4 casos nuevos en
el dataset de evaluación (`tests/eval/dataset.py`)

**Plataforma objetivo**: local y Streamlit Community Cloud (igual que la 001)

**Tipo de proyecto**: single project

**Restricciones**: solo lectura para el agente (la carga de las tablas es un script de setup);
sin inventar datos (Principio I); sin país ni jugadores sintéticos para campeones históricos

**Escala/Alcance**: 44 personas, 58 campeonatos, 3 PDFs (~1.600 chunks en total con los 2 previos)

## Verificación de constitución

| Principio | ¿Cumple el plan? |
|---|---|
| I. Grounding-first | ✅ Datos con fuente declarada; el agente rehúsa lo que no está (2026, país, Siciliana) |
| II. Seguridad y solo lectura | ✅ El agente sigue con conexión de solo lectura; la carga es un script aparte |
| III. Verificabilidad (test-first) | ⚠️ Pruebas de integridad y casos de evaluación presentes, pero escritas junto con el código, no antes |
| IV. Observabilidad | ✅ Sin cambios: las trazas de LangSmith cubren las rutas nuevas |
| V. Reproducibilidad y documentación | ✅ Datos versionados en código; `championships.py` recarga sin tocar el resto; ADR 0006 |
| VI. Simplicidad (YAGNI) | ✅ Se descartó el país, `notes` y un id sin uso; el vínculo con `players` es opcional |

**Resultado**: una desviación (III, tests escritos en paralelo). No requiere Complexity Tracking.

## Estructura del proyecto

### Documentación (esta funcionalidad)

```text
specs/002-world-champions-data/
├── plan.md          # Este archivo
├── spec.md          # Qué y por qué
├── research.md      # Decisiones e investigación
├── data-model.md    # Tablas y relaciones
├── quickstart.md    # Cómo cargar y verificar
└── tasks.md         # Tareas (hechas y pendientes)
```

### Código fuente (cambios respecto de la 001)

```text
src/chess_agent/
├── db/
│   ├── championships.py   # datos + DDL + carga independiente (python -m chess_agent.db.championships)
│   ├── schema.sql         # 8 tablas (champions, world_championships, players.fide_id)
│   └── seed.py            # carga champions/world_championships junto con el resto
├── nodes/router.py        # datos de campeones → SQL; historia y récords → RAG
├── sql/generator.py       # few-shot con JOIN y reglas de mapeo; reinados → NO_SQL
└── rag/
    ├── ingest.py          # CHUNK_WORDS 70, OVERLAP_WORDS 15
    └── retriever.py       # DEFAULT_K 8
data/pdfs/                 # + list-of-world-chess-championships, world-chess-championship,
                           #   campeonato-mundial-de-ajedrez
tests/unit/test_championships.py
docs/decisions/0006-tamano-de-chunk-y-k.md
```

**Decisión de estructura**: se extiende la estructura existente; no se crean paquetes nuevos.

## Decisiones de diseño clave

1. **SQL para los datos, RAG para el contexto.** Las tablas de los PDFs salen partidas en líneas
   sueltas al extraer el texto y el RAG las resolvía mal; los hechos con respuesta exacta van a
   tablas.
2. **`champions` separada de `players`.** `players` alimenta las partidas sintéticas: meter a los
   campeones históricos ahí los pondría a jugar torneos de 2023. El vínculo es opcional y por
   FIDE ID.
3. **Chunks de 70 palabras, `k = 8`.** El modelo de embeddings solo lee 128 tokens.

## Complexity Tracking

Sin violaciones que justificar.
