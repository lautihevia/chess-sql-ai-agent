# Especificación de funcionalidad: Datos de campeonatos mundiales de ajedrez

**Rama de la funcionalidad**: `002-world-champions-data` (implementada en la rama `feat/world-champions-pdfs`, PR #1)

**Creada**: 2026-10-11

**Estado**: Implementada (especificación retroactiva)

> **Nota:** esta spec se escribió *después* de construir la funcionalidad, a pedido de la revisión
> de la PR, para dejarla documentada con el mismo formato que [`001-sql-rag-agent`](../001-sql-rag-agent/spec.md).
> Describe lo que se construyó y cómo se verificó; no guió la implementación.

**Entrada**: Descripción del usuario: "Agregar PDFs sobre los campeones del mundo de ajedrez (años, cuándo salieron campeones, etc.) para que el agente pueda responder sobre ellos."

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Datos de campeonatos mundiales (Prioridad: P1)

Una persona pregunta por hechos concretos de los campeonatos mundiales (quién fue campeón en un
año, contra quién, con qué marcador, cuántos títulos ganó alguien, cuántos años vivió) y recibe la
respuesta correcta, sin necesidad de conocer las tablas.

**Por qué esta prioridad**: son las preguntas que motivaron la funcionalidad ("años, cuándo
salieron campeones") y tienen una respuesta exacta y verificable.

**Prueba independiente**: preguntar "¿quién fue campeón del mundo en 1972 y a quién derrotó?" y
verificar que responde Fischer, contra Spassky, 12½–8½.

**Escenarios de aceptación**:

1. **Dado** el historial de campeonatos, **Cuando** se pregunta por el campeón de un año con match,
   **Entonces** responde el ganador, el rival y el marcador.
2. **Dado** un año sin match (p. ej. 1950), **Cuando** se pregunta quién era campeón,
   **Entonces** responde quien ganó el último match anterior.
3. **Dado** un campeón, **Cuando** se pregunta cuántos títulos ganó o cuántos años vivió,
   **Entonces** responde el número correcto (Kasparov: 6; Capablanca: 54).
4. **Dado** que hay campeones que también están en la lista de jugadores, **Cuando** se pregunta por
   su rating, **Entonces** el sistema cruza ambas fuentes (Carlsen: 2882).

---

### Historia de usuario 2 - Historia narrada del campeonato (Prioridad: P2)

Una persona pregunta el *porqué* de un hecho (la ruptura de 1993, la renuncia de Fischer en 1975,
por qué Carlsen no defendió el título en 2023) y recibe una respuesta apoyada en los documentos,
con la fuente citada.

**Por qué esta prioridad**: complementa los datos con contexto; depende de que el RAG recupere el
fragmento correcto.

**Prueba independiente**: preguntar "¿por qué perdió Fischer el título en 1975?" y verificar que la
respuesta cita el documento y explica la disputa por el formato del match.

**Escenarios de aceptación**:

1. **Dado** una pregunta causal sobre un campeonato, **Cuando** se consulta, **Entonces** el router
   la envía al RAG y la respuesta cita la fuente y la página.
2. **Dado** una pregunta que mezcla dato y contexto ("¿quién fue campeón en 1972 y por qué fue tan
   importante ese match?"), **Cuando** se consulta, **Entonces** se combinan SQL y RAG.
3. **Dado** una pregunta sobre un récord histórico (el reinado más largo), **Cuando** se consulta,
   **Entonces** se responde desde los documentos (Lasker, 27 años) y no se calcula desde la tabla.

---

### Historia de usuario 3 - Rechazo honesto cuando falta información (Prioridad: P3)

Cuando el dato no está en las fuentes, el sistema lo dice en lugar de inventar.

**Por qué esta prioridad**: protege el principio de grounding del proyecto.

**Prueba independiente**: preguntar por el campeonato de 2026 o por "los campeones soviéticos".

**Escenarios de aceptación**:

1. **Dado** un campeonato sin resultado cargado (2026) o fuera del rango (1850), **Cuando** se
   pregunta, **Entonces** responde que no encontró la información.
2. **Dado** un atributo que no se almacena (el país de un campeón), **Cuando** se pregunta,
   **Entonces** rehúsa en lugar de suponer.
3. **Dado** una pregunta cuyo contenido no está en los documentos (la Defensa Siciliana),
   **Cuando** se consulta, **Entonces** rehúsa.

---

### Casos límite

- Entre 1993 y 2006 hubo dos títulos rivales (clásico y FIDE): cada campeonato indica su línea
  (`title_line`) y "campeón en el año X" usa la línea principal.
- El match de 1975 no se jugó (Fischer no se presentó): `score` queda vacío.
- Un mismo año puede tener más de un campeonato (1910, 1993, 2000, 2004).
- Los reinados no se pueden calcular con la tabla (dependen de quién derrotó a quién): el
  generador de SQL devuelve `NO_SQL` y la pregunta va a los documentos.
- Preguntas en español sobre documentos mayormente en inglés: la recuperación es más débil (ver
  `research.md`).

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **RF-001**: El sistema DEBE almacenar el historial de campeonatos mundiales 1886-2024 (año, sede,
  ganador, rival, marcador, línea del título, formato) y las personas que los jugaron.
- **RF-002**: El sistema DEBE responder con SQL las preguntas de datos sobre campeonatos y sobre las
  personas (nacimiento, fallecimiento, edad, cantidad de títulos).
- **RF-003**: El router DEBE enviar a SQL los datos de campeones y a RAG la historia narrada y los
  récords.
- **RF-004**: El sistema DEBE vincular, cuando exista, a cada campeón con su registro en `players`
  usando un identificador estándar (FIDE ID) y no el nombre.
- **RF-005**: El sistema NO DEBE inventar jugadores sintéticos para los campeones históricos ni
  asignarles un país.
- **RF-006**: Los datos DEBEN indicar su fuente (campeonatos: PDF de Wikipedia; años de
  nacimiento y muerte: Wikidata; FIDE ID: Wikidata contrastado con ratings.fide.com).
- **RF-007**: El RAG DEBE poder recuperar información de cualquier parte de un fragmento
  (los fragmentos deben caber en la ventana del modelo de embeddings).
- **RF-008**: Se DEBEN incorporar los PDFs de referencia sobre campeonatos mundiales (lista de
  campeonatos, historia general y versión en español) al repositorio documental.
- **RF-009**: La carga de las tablas DEBE ser reproducible e independiente del resto de la base.

### Entidades clave *(incluye por involucrar datos)*

- **Campeón / persona (`champions`)**: persona que jugó un campeonato mundial; nombre, años de
  nacimiento y muerte, FIDE ID (si existe) y vínculo opcional con `players`.
- **Campeonato mundial (`world_championships`)**: un match o torneo por el título; año, sede,
  ganador, rival, marcador, número de título del ganador, línea del título y formato.
- **Documento de referencia**: los tres PDFs de campeonatos agregados a `data/pdfs/`.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **CE-001**: Las preguntas de datos de campeones del conjunto de prueba se responden
  correctamente (3 casos en el dataset de evaluación: 100%).
- **CE-002**: El enrutamiento se mantiene en 100% sobre los 22 casos de evaluación.
- **CE-003**: La fidelidad RAG sube respecto de la línea base (38% → 62% sobre los mismos
  documentos) y los rehúsos correctos se mantienen en 100%.
- **CE-004**: Cada vínculo `champions`–`players` coincide por FIDE ID (8 de 44), sin nombres
  inventados.
- **CE-005**: Las pruebas unitarias de integridad de los datos pasan sin base ni API.

## Supuestos

- Los datos de campeonatos son reales y se toman de un PDF (Wikipedia, CC BY-SA); el resto del
  seed sigue siendo sintético.
- El campeón actual es el que figura en las fuentes (Gukesh, 2024); el match de 2026 no tiene
  resultado en el PDF y no se carga.
- Los campeones históricos anteriores al sistema de ratings no tienen FIDE ID y quedan sin vínculo
  con `players`.
- Fuera de alcance: cargar partidas reales desde archivos PGN (feature aparte), país de los
  campeones y duración de reinados.
