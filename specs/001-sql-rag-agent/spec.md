# Especificación de funcionalidad: Agente de ajedrez con SQL + RAG

**Rama de la funcionalidad**: `001-sql-rag-agent`

**Creada**: 2026-09-26

**Estado**: Borrador

**Entrada**: Descripción del usuario: "Agente de IA que responde preguntas en lenguaje natural sobre partidas de ajedrez combinando consultas a una base de datos relacional (SQL) y recuperación de documentos (RAG), decidiendo la fuente automáticamente"

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Consultas sobre datos de partidas (Prioridad: P1)

Una persona interesada en ajedrez hace una pregunta en lenguaje natural sobre datos concretos
(jugadores, partidas, resultados, aperturas, torneos, ratings) y recibe una respuesta correcta
basada en la información almacenada, sin necesidad de saber consultar una base de datos.

**Por qué esta prioridad**: Es el núcleo del sistema y aporta valor por sí solo; un asistente
que responde correctamente preguntas de datos ya es un producto mínimo viable.

**Prueba independiente**: Se puede probar por completo formulando preguntas de datos (p. ej.
"¿cuántas partidas ganó Carlsen con blancas?") y verificando que la respuesta coincide con el
dato real.

**Escenarios de aceptación**:

1. **Dado** que existen partidas de un jugador, **Cuando** el usuario pregunta cuántas ganó con
   blancas, **Entonces** el sistema responde con el conteo correcto.
2. **Dado** el conjunto de jugadores, **Cuando** el usuario pide el top 5 por rating, **Entonces**
   el sistema devuelve cinco jugadores ordenados correctamente.
3. **Dado** un jugador inexistente, **Cuando** se pregunta por sus partidas, **Entonces** el
   sistema informa que no hay datos, sin inventar un número.

---

### Historia de usuario 2 - Consultas sobre reglas y teoría (Prioridad: P2)

El usuario pregunta sobre conocimiento conceptual del ajedrez (reglas oficiales, ideas de
aperturas) y recibe una respuesta fundamentada en los documentos de referencia, con su cita.

**Por qué esta prioridad**: Completa la propuesta de valor (dos tipos de conocimiento en una
sola interfaz) y es requisito del trabajo; depende de tener antes una base de respuestas funcional.

**Prueba independiente**: Se prueba preguntando por una regla o idea cubierta por los documentos
y verificando que la respuesta es correcta y cita la fuente.

**Escenarios de aceptación**:

1. **Dado** un documento de reglas, **Cuando** el usuario pregunta por una regla, **Entonces** el
   sistema responde correctamente citando el documento.
2. **Dado** un texto de teoría, **Cuando** el usuario pregunta por la idea de una apertura,
   **Entonces** el sistema la explica citando la fuente.
3. **Dado** un tema fuera de los documentos, **Cuando** se pregunta por él, **Entonces** el
   sistema informa que no está en los documentos disponibles.

---

### Historia de usuario 3 - Enrutamiento, consultas mixtas y multilingüe (Prioridad: P3)

El sistema decide automáticamente la fuente adecuada, combina ambas cuando la pregunta lo
requiere, y funciona con preguntas en español e inglés.

**Por qué esta prioridad**: Es el diferencial de "agente" (decidir la fuente) y mejora la
experiencia, pero se apoya en las dos historias anteriores ya funcionando.

**Prueba independiente**: Se prueba con preguntas puramente de datos, puramente conceptuales,
mixtas y en ambos idiomas, verificando que se elige la fuente correcta y la respuesta es adecuada.

**Escenarios de aceptación**:

1. **Dado** una pregunta de datos, **Cuando** se envía, **Entonces** el sistema la resuelve con la
   base de datos y no con los documentos.
2. **Dado** una pregunta conceptual, **Cuando** se envía, **Entonces** el sistema la resuelve con
   los documentos y no con la base de datos.
3. **Dado** una pregunta mixta, **Cuando** se envía, **Entonces** el sistema combina ambas fuentes
   en una respuesta coherente.
4. **Dado** una pregunta en inglés, **Cuando** se envía, **Entonces** el sistema responde
   correctamente en inglés.

### Casos límite

- ¿Qué pasa cuando la consulta de datos no devuelve resultados? → El sistema informa que no hay
  datos que cumplan la condición, sin suponer valores.
- ¿Cómo maneja una pregunta ambigua entre las dos fuentes? → Puede consultar ambas y combinar.
- ¿Qué ocurre ante un intento de manipulación ("borrá los datos")? → El sistema rechaza cualquier
  operación que no sea de lectura.
- ¿Qué pasa si la información no está en ninguna fuente? → El sistema se rehúsa honestamente.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **RF-001**: El sistema DEBE aceptar preguntas en lenguaje natural en español e inglés.
- **RF-002**: El sistema DEBE decidir automáticamente si una pregunta se responde con datos
  estructurados, con conocimiento documental o con ambos.
- **RF-003**: El sistema DEBE responder preguntas sobre datos de ajedrez (jugadores, partidas,
  resultados, aperturas, torneos, ratings) de forma correcta y basada en la información almacenada.
- **RF-004**: El sistema DEBE responder preguntas conceptuales (reglas, ideas de aperturas)
  fundamentándose en los documentos de referencia y citando la fuente.
- **RF-005**: El sistema DEBE combinar ambas fuentes cuando la pregunta lo requiera.
- **RF-006**: El sistema DEBE rehusarse a responder cuando no haya evidencia suficiente, en lugar
  de inventar.
- **RF-007**: El sistema DEBE rechazar cualquier solicitud que implique modificar o eliminar datos.
- **RF-008**: El sistema DEBE responder en el mismo idioma que la pregunta.
- **RF-009**: El sistema DEBE ofrecer una forma de interacción conversacional para que el usuario
  formule sus preguntas y vea las respuestas.
- **RF-010**: El sistema DEBE permitir inspeccionar cómo se obtuvo cada respuesta (fuente usada y
  fundamento) para su verificación.

### Entidades clave *(incluye por involucrar datos)*

- **Jugador**: persona que disputa partidas; atributos como nombre, país, título y rating.
- **Apertura**: secuencia inicial con nombre y código de clasificación.
- **Torneo**: competencia que agrupa partidas, con sede y fechas.
- **Partida**: enfrentamiento entre dos jugadores, con resultado, apertura y torneo asociados.
- **Jugada**: cada movimiento dentro de una partida.
- **Historial de rating**: evolución del rating de un jugador en el tiempo.
- **Documento de referencia**: material textual (reglas, teoría) usado para responder preguntas
  conceptuales.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **CE-001**: El sistema elige la fuente correcta (datos, documentos o ambos) en al menos el 90%
  de un conjunto de preguntas de prueba.
- **CE-002**: Al menos el 90% de las preguntas de datos del conjunto de prueba obtienen una
  respuesta correcta.
- **CE-003**: El 100% de las respuestas conceptuales incluyen una cita de la fuente.
- **CE-004**: El 100% de las preguntas sin evidencia disponible resultan en un rehúso, sin datos
  inventados.
- **CE-005**: El 100% de los intentos de modificar o eliminar datos son rechazados.
- **CE-006**: El usuario obtiene una respuesta en un tiempo razonable para una interacción
  conversacional (objetivo orientativo: menos de 10 segundos).
- **CE-007**: Preguntas equivalentes en español e inglés obtienen respuestas correctas.

## Supuestos

- Los datos de ajedrez son sintéticos y suficientes para que las consultas sean significativas;
  no se requiere exactitud histórica.
- Los documentos de referencia son públicos (reglas oficiales y teoría de aperturas).
- No se requiere autenticación de usuarios ni gestión de cuentas.
- El sistema es de solo lectura sobre los datos: no se editan datos desde la conversación.
- El alcance no incluye análisis de posiciones ni motor de ajedrez.
