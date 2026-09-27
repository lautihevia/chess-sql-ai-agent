# Glosario

Términos de dominio (ajedrez) y técnicos (IA/ingeniería) usados en el proyecto.

## Ajedrez

| Término | Definición |
|---|---|
| **ELO / rating** | Puntaje numérico que mide la fuerza de un jugador. Mayor = mejor. |
| **Título** | Distinción FIDE: GM (Gran Maestro), IM (Maestro Internacional), FM (Maestro FIDE), WGM/WIM (femeninos), CM, etc. |
| **ECO** | *Encyclopedia of Chess Openings*: código que clasifica aperturas (ej. `B90` = Siciliana Najdorf). |
| **Apertura** | Secuencia inicial de jugadas con nombre propio (ej. Defensa Siciliana). |
| **Jugada / movimiento (move)** | Un turno completo: una jugada de blancas + una de negras. |
| **Media jugada / ply** | Una sola jugada de un color. Un movimiento = 2 plies. En la BD, `moves` guarda **una fila por ply**. |
| **SAN** | *Standard Algebraic Notation*: notación de una jugada (ej. `Nf3`, `O-O`, `exd5`). |
| **Resultado** | `1-0` (ganan blancas), `0-1` (ganan negras), `1/2-1/2` (tablas/empate). |
| **Tablas** | Empate. |

## IA / Ingeniería

| Término | Definición |
|---|---|
| **LLM** | *Large Language Model*. Aquí, Claude vía API. |
| **Text-to-SQL** | Traducir una pregunta en lenguaje natural a una consulta SQL. |
| **RAG** | *Retrieval-Augmented Generation*: recuperar fragmentos relevantes de documentos y usarlos como contexto para responder. |
| **Embedding** | Representación numérica (vector) de un texto; textos parecidos → vectores cercanos. |
| **Chunk** | Fragmento en que se parte un documento para indexarlo. |
| **Vector store** | Base que almacena embeddings y permite búsqueda por similitud (aquí, pgvector en Supabase). |
| **Routing** | Decisión del agente sobre qué fuente usar (SQL, RAG o ambas). |
| **Nodo** | Paso del grafo del agente (LangGraph). |
| **Guardrail** | Restricción de seguridad (ej. permitir solo `SELECT`). |
| **Grounding** | Que la respuesta se apoye en evidencia real (resultado SQL o fragmento recuperado), no inventada. |
| **Alucinación / delirio** | Respuesta inventada sin fundamento en los datos. |
| **SDD** | *Spec-Driven Development*: desarrollo guiado por especificación (aquí, GitHub Spec Kit). |
