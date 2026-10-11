# ADR 0006 — Tamaño de chunk (70 palabras, solape 15) y `k = 8`

- **Estado:** aceptada
- **Fecha:** 2026-10-11

## Contexto

El RAG parte cada PDF en chunks, los convierte en vectores y, ante una pregunta, recupera los
`k` más parecidos (ver [ADR 0004](0004-embeddings-locales.md) y [ADR 0005](0005-pgvector.md)).

El modelo de embeddings, `paraphrase-multilingual-MiniLM-L12-v2`, tiene `max_seq_length = 128`:
solo "lee" los primeros 128 tokens de cada texto y descarta el resto sin avisar. Los chunks
anteriores eran de 250 palabras con solape de 50 (antes habían sido de 600; se bajaron a 250 para
separar mejor los artículos cortos de las Leyes FIDE). Al agregar los PDFs de campeonatos
mundiales, preguntas como "¿qué es la PCA y por qué se creó?" no recuperaban el fragmento que
contenía la respuesta, aunque estaba indexado.

Se midió con el tokenizer del propio modelo sobre los 5 PDFs: **el 91% de los chunks de 250
palabras superaba los 128 tokens**, es decir, su vector representaba solo la primera mitad del
texto y lo que estaba en el medio no se podía encontrar.

## Decisión

- `CHUNK_WORDS = 70` y `OVERLAP_WORDS = 15` (`src/chess_agent/rag/ingest.py`).
- `DEFAULT_K = 8` (`src/chess_agent/rag/retriever.py`).

## Alternativas consideradas

### Tamaño de chunk (medido)

| Palabras / solape | Chunks totales | Chunks que superan los 128 tokens |
|---|---|---|
| 250 / 50 (anterior) | 498 | 91% |
| 100 / 20 | 1.120 | 59% |
| 90 / 20 | 1.263 | 35% |
| 80 / 20 | 1.447 | 16% |
| **70 / 15 (elegida)** | 1.605 | **9%** |
| 60 / 15 | 1.919 | 7% |

- **60 palabras:** casi no mejora la truncación (de 9% a 7%) y agrega ~20% más de chunks.
- **80 palabras o más:** entre el 16% y el 59% de los chunks seguía truncado.
- El ~9% que queda por encima de 128 tokens son sobre todo tablas y listas de referencias, que
  tienen muchos tokens por palabra; ningún tamaño razonable lo evita.

### Solape

Se mantuvo la proporción que ya había (50 de 250 = 20%; 15 de 70 ≈ 21%) para que una idea cortada
en el límite de un chunk quede completa en el siguiente. **No se probaron otros valores de solape**:
es una decisión por proporción, no por medición.

### Valor de `k`

Con chunks de 70 palabras, `k = 4` aportaba ~280 palabras de contexto (antes, 4 × 250 = 1.000).
Se subió a 8 (~560 palabras). Con `k = 4`, por ejemplo, "¿por qué Fischer perdió el título en 1975?"
dejó de responderse; con `k = 8` volvió a responder. En una prueba de recuperación de 14
preguntas, `k = 4` y `k = 6` acertaron 8 y `k = 8` acertó 9. No se evaluaron valores mayores.

### Alternativas descartadas por ahora (no se probaron)

- **Cambiar de modelo a uno con ventana más larga** (por ejemplo, `multilingual-e5`, 512 tokens):
  permitiría chunks más grandes, pero es más pesado y requiere revisar la dimensión del vector
  (hoy 384) y reindexar todo. Queda como mejora futura.
- **Partir por oraciones o párrafos en vez de por cantidad de palabras:** respetaría mejor los
  límites del texto, pero agrega complejidad y los PDFs extraídos tienen saltos de línea poco
  fiables.
- **Traducir la pregunta al inglés antes de recuperar:** atacaría otro problema (el modelo separa
  mal los idiomas; "rey ahogado" no recupera "stalemate"), no el de la ventana de 128 tokens.

## Resultados

Evaluación local sobre 22 casos, mismos documentos y misma BD:

| Métrica | Con 250 palabras, `k = 4` | Con 70 palabras, `k = 8` |
|---|---|---|
| Fidelidad RAG (con cita) | 38% (3/8) | **62% (5/8)** |
| Enrutamiento | 100% | 100% |
| Exactitud SQL | 100% | 100% |
| Rehúso correcto | 100% | 100% |
| Latencia media | 4,4 s | 5,2 s |

De los 3 casos RAG que siguen fallando, 2 (la Defensa Siciliana) preguntan algo que no está en
los documentos indexados —el agente rehúsa, que es lo correcto— y 1 ("rey ahogado" en español) es
una limitación del modelo entre idiomas.

## Consecuencias

- (+) Los datos del medio de cada chunk vuelven a ser recuperables.
- (−) Hay ~3 veces más chunks (de 498 a 1.605): indexar todo tarda ~1 min 20 s y la tabla
  `document_chunks` crece.
- (−) Cada consulta trae más fragmentos (8 en vez de 4), aunque más cortos; la latencia subió
  ~0,8 s en la evaluación.
- (−) Cambiar `CHUNK_WORDS` obliga a volver a correr la ingesta en las bases existentes.
- (−) El tamaño ideal depende del modelo y de los documentos: si cambia alguno, hay que volver a
  medir qué porcentaje de chunks supera la ventana del modelo (contando tokens con su tokenizer).
