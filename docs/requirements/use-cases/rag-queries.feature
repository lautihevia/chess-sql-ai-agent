# language: es
Característica: Consultas sobre conocimiento textual (ruta RAG)
  Como usuario
  Quiero preguntar sobre reglas e ideas de ajedrez
  Para obtener respuestas fundamentadas en los documentos, con su cita

  Antecedentes:
    Dado que el repositorio RAG contiene las Leyes FIDE y un texto de teoría de aperturas

  Escenario: Consulta sobre una regla FIDE
    Cuando el usuario pregunta "¿qué establece la regla de la pieza tocada?"
    Entonces el agente recupera fragmentos de las Leyes FIDE
    Y la respuesta explica la regla citando el documento fuente

  Escenario: Consulta sobre la idea de una apertura
    Cuando el usuario pregunta "¿cuál es la idea estratégica de la Defensa Siciliana?"
    Entonces el agente recupera fragmentos del texto de teoría de aperturas
    Y la respuesta describe la idea citando la fuente

  Escenario: Cita de la fuente
    Cuando el agente responde una consulta por la ruta RAG
    Entonces la respuesta incluye una referencia al documento del que se obtuvo la información

  Escenario: Rehúso cuando el tema no está en los documentos
    Cuando el usuario pregunta "¿cuál es la mejor computadora para jugar al ajedrez?"
    Entonces el agente responde que no encontró información en los documentos disponibles
    Y no inventa una respuesta
