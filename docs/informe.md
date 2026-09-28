# Informe técnico — Agente de ajedrez con SQL + RAG

**Trabajo Práctico Integrador — AI Engineering** · Ingeniería en Informática (5.º año)

> Borrador generado a partir de la documentación del proyecto. Revisar, ajustar extensión (≤10
> páginas) e insertar las capturas indicadas antes de entregar.

---

## 1. Introducción

El objetivo del TP es construir un **"SQL AI Agent"**: un asistente que recibe preguntas en
lenguaje natural (español o inglés) sobre partidas de ajedrez y responde decidiendo por sí mismo
de qué fuente obtener el contexto (*routing*):

1. una **base de datos relacional**, traduciendo la pregunta a SQL (*text-to-SQL*);
2. un **repositorio documental**, mediante **RAG** sobre PDFs (Leyes FIDE + teoría de aperturas).

El dominio elegido es el ajedrez. La solución es un grafo de agente (router → SQL/RAG → síntesis)
orquestado con **LangGraph**, con **Claude** como motor de razonamiento, embeddings locales,
**PostgreSQL + pgvector** en **Supabase**, interfaz **Streamlit** y observabilidad con
**LangSmith**. El énfasis está en respuestas **fundamentadas** (sin alucinación) y en el acceso
de **solo lectura** a los datos.

## 2. Modelo de datos

La base tiene **6 tablas** relacionales (datos sintéticos, generados con semilla fija para
reproducibilidad):

| Tabla | Descripción | Claves |
|---|---|---|
| `players` | Jugadores (nombre, país, año, título, peak_rating) | PK `player_id` |
| `openings` | Aperturas (código ECO, nombre, primeras jugadas) | PK `opening_id` |
| `tournaments` | Torneos (nombre, sede, fechas, formato) | PK `tournament_id` |
| `games` | Partidas (blancas, negras, apertura, resultado, nº jugadas) | PK `game_id`, FKs |
| `moves` | Jugadas, **una fila por media jugada (ply)** | PK `move_id`, FK `game_id` (indexada) |
| `player_ratings` | Historial de rating por jugador y fecha | PK `rating_id`, FK `player_id` |

Restricciones de integridad clave: `result ∈ {1-0, 0-1, 1/2-1/2}`, `color ∈ {white, black}`,
blancas ≠ negras en cada partida, e integridad referencial en todas las FK. Se agrega un índice
en `moves.game_id` (ADR 0003) para reconstruir partidas de forma eficiente. Volúmenes cargados:
30 jugadores, 20 aperturas, 15 torneos, 150 partidas, ~9.000 jugadas y 180 ratings.

> **Evidencia:** insertar el diagrama ER (`docs/data/data-model.md`).

## 3. Arquitectura del agente

El agente es un grafo **LangGraph** con router explícito:

```
pregunta ─► router ─┬─ SQL   ─► sql_node ───────────────► síntesis ─► respuesta
                    ├─ RAG   ─► rag_node ───────────────► síntesis ─► respuesta
                    └─ AMBAS ─► sql_node ─► rag_node ────► síntesis ─► respuesta
```

- **Router**: clasifica la pregunta en `SQL`, `RAG` o `AMBAS` con Claude y detecta el idioma.
- **Nodo SQL**: genera SQL con Claude (inyectando el esquema real, ejemplos *few-shot* de
  *golden queries* y un mapeo de términos) → **valida** (solo lectura) → ejecuta → **reintenta
  una vez** con el mensaje de error si falla.
- **Nodo RAG**: embebe la pregunta y recupera los *top-k* fragmentos por similitud coseno en
  pgvector, con **recall alto**; adjunta la fuente y la página de cada fragmento.
- **Nodo Síntesis**: redacta la respuesta usando **solo** la evidencia (resultado SQL y/o
  fragmentos). Si la evidencia no alcanza, rehúsa (patrón *LLM-as-judge* con sentinel
  `NO_ANSWER`). Responde en el idioma de la pregunta y cita las fuentes en las respuestas RAG.

La rama **AMBAS** ejecuta SQL y luego RAG, y la síntesis combina ambos insumos manteniendo la
trazabilidad de cada parte.

> **Evidencia:** insertar el diagrama de arquitectura (`docs/architecture/container-view.md`).

## 4. Decisiones técnicas

Resumen de los ADR (`docs/decisions/`):

| Tema | Decisión | Racional |
|---|---|---|
| Orquestación | LangGraph con router explícito | Control y trazabilidad; cumple el criterio agéntico |
| Base de datos | PostgreSQL en Supabase | Nube gratuita, editor visual, pgvector integrado |
| Modelado de jugadas | Una fila por *ply*, indexada | Consultas a nivel jugada sin costo relevante |
| Embeddings | `sentence-transformers` local (multilingüe) | Gratis, sin API extra, soporta español |
| Vector store | pgvector en Supabase | Todo en una sola BD en la nube |
| LLM | `claude-haiku-4-5` en todos los nodos | Presupuesto acotado (~US$3); alcanza para estas tareas |

Medidas de ahorro de costo: `max_tokens` chico por nodo (router ~8, SQL ~512, síntesis ~500),
sin *extended thinking* y embeddings locales (sin costo de API). Conexión a Supabase por el
**Session Pooler (IPv4)**, ya que la conexión directa es IPv6-only en el *free tier*.

## 5. Anti-alucinación y seguridad

**Grounding (Principio I):** toda afirmación se apoya en evidencia verificable. La síntesis
responde solo con las filas SQL reales o los fragmentos recuperados; si no hay evidencia
suficiente, rehúsa explícitamente en lugar de inventar. Las respuestas RAG **citan** el documento
y la página.

**Seguridad y solo lectura (Principio II):** dos capas de defensa.

1. **Validador SQL**: acepta una única sentencia `SELECT` (o `WITH ... SELECT`), agrega un
   `LIMIT` de seguridad y **rechaza** escrituras, DDL, múltiples sentencias e inyecciones
   (`INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/…`, `SELECT ... INTO`, *stacked queries*).
2. **Conexión de solo lectura**: la BD se abre en modo `read_only`; cualquier escritura que se
   colara es rechazada por PostgreSQL (`ReadOnlySqlTransaction`), con `statement_timeout` acotado.

Se cubre con `tests/unit/test_security.py` (incluye 12 *payloads* maliciosos) y con el escenario
BDD de rechazo de escritura.

## 6. Ejemplos de consultas

De la validación real (`docs/quickstart-validation.md`):

| Pregunta | Ruta | Resultado |
|---|---|---|
| ¿Cuántas partidas ganó Carlsen con blancas? | SQL | "Carlsen ganó 4 partidas con blancas" (+ SQL generado) |
| ¿Qué dice la regla FIDE sobre tocar una pieza? | RAG | Explica la regla *touch-move*, cita `fide-laws (p.3)` |
| how many draws are there? | SQL | "there are 32 draws" (responde en inglés) |
| ¿Cuál es la mejor computadora de ajedrez? | RAG | Rehúsa: "no encontré esa información en los documentos" |
| Borrá la tabla games | SQL | Rechaza: "solo puedo realizar consultas de lectura" |

> **Evidencia:** insertar capturas de la app (Streamlit) para cada caso.

## 7. Pruebas y evaluación

**Pruebas automatizadas:**
- **33** pruebas unitarias (validador SQL + seguridad), sin costo de API.
- **14** escenarios BDD (Gherkin) end-to-end: 6 SQL, 4 RAG, 4 routing.
- Linting con `ruff`.

**Evaluación sistemática (LangSmith)** sobre un dataset de 18 casos curados (SQL, RAG, mixtos y
de rehúso, en español e inglés):

| Métrica | Resultado |
|---|---|
| Exactitud de enrutamiento | **100%** (18/18) |
| Exactitud SQL | **100%** (8/8) |
| Fidelidad RAG (con cita) | **100%** (7/7) |
| Tasa de rehúso correcto | **100%** (4/4) |
| Latencia media | ~4,8 s por consulta |

Ajuste relevante durante la evaluación: se pasó de un umbral de similitud fijo (que descartaba
reformulaciones válidas) a **recall alto + juicio del LLM** (`NO_ANSWER`), lo que subió la
fidelidad RAG de 86% a 100% sin degradar los rehúsos.

> **Evidencia:** insertar capturas de trazas de LangSmith (un caso correcto y uno de rehúso) y
> del experimento `chess-agent-eval`.

## 8. Despliegue

**App en producción:** https://chess-ai-sql-ucse.streamlit.app/

- **Base de datos:** Supabase (PostgreSQL + pgvector) en la nube, acceso por SSL.
- **App + agente:** Streamlit Community Cloud, conectado al repositorio de GitHub (redeploy
  automático en cada *push*); los secretos se cargan en *App settings → Secrets*.
- **SaaS:** Claude API (Anthropic) y LangSmith.

Reproducibilidad: `uv sync`, seed determinista e ingesta idempotente de PDFs (ver README).

## 9. Conclusiones

Se construyó un agente que responde preguntas de ajedrez combinando text-to-SQL y RAG, con
enrutamiento automático, soporte bilingüe, respuestas fundamentadas y acceso de solo lectura.

**Criterios de promoción cubiertos (5/5):**

| Criterio | Cómo se cubre |
|---|---|
| Despliegue en la nube | Supabase (BD) + Streamlit Community Cloud (app) |
| Interfaz de usuario | App Streamlit con detalle de ruta, SQL y fuentes |
| Framework agéntico | LangGraph (router → SQL/RAG → síntesis) |
| Observabilidad y evaluación | LangSmith (trazas + experimento con métricas) |
| Desarrollo dirigido por especificación (SDD) | GitHub Spec Kit (constitution, spec, plan, tasks) |

**Mejoras futuras:** reemplazar los PDFs de muestra por los documentos oficiales completos,
probar un modelo de embeddings con mayor separación (p. ej. *multilingual-e5*), *prompt caching*
del prefijo estático del nodo SQL para reducir costos, y ampliar el dataset de evaluación.
