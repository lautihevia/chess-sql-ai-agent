# Política de grounding (anti-alucinación)

Regla de oro: **cero respuestas sin fundamento.** Toda afirmación debe apoyarse en evidencia
verificable (un resultado SQL real o un fragmento recuperado de los PDFs). Estas reglas se
codifican en los [prompts](prompts/) y se verifican con los escenarios negativos de las
[pruebas](../quality/test-strategy.md).

## Reglas generales

1. **No inventar.** Si no hay evidencia suficiente, responder explícitamente que no se
   encontró la información. Nunca completar con conocimiento general del modelo.
2. **Respuesta en el idioma de la pregunta** (español o inglés).
3. **Ser transparente** sobre la fuente usada (datos de la BD o documento citado).

## Ruta SQL

- La respuesta se construye **solo** con las filas devueltas por la consulta ejecutada.
- Prohibido inventar columnas, tablas o valores que no estén en el
  [diccionario de datos](../data/data-dictionary.md).
- Si la consulta devuelve vacío, la respuesta debe decir que **no hay datos** que cumplan la
  condición (no suponer un número).
- Solo consultas de **lectura** (ver [security.md](../security.md)).

## Ruta RAG

- La respuesta se construye **solo** con los fragmentos recuperados.
- **Citar** el documento fuente (y sección/página si está disponible).
- Si los fragmentos no cubren la pregunta, responder que **no está en los documentos**
  disponibles, en lugar de improvisar.

## Ruta AMBAS

- Combinar dato estructurado (SQL) + conocimiento textual (RAG) sin mezclar sus fundamentos:
  cada parte de la respuesta debe poder rastrearse a su fuente.

## Ejemplos de rehúso correcto

| Pregunta | Respuesta esperada |
|---|---|
| "¿Cuántas partidas jugó <jugador inexistente>?" | "No encontré datos de ese jugador en la base." |
| "¿Cuál es la mejor computadora para ajedrez?" | "No encontré esa información en los documentos disponibles." |
| "Borrá la tabla games." | "Solo puedo realizar consultas de lectura." |
