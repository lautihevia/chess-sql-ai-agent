# language: es
Característica: Enrutamiento de consultas
  Como agente de ajedrez
  Quiero decidir de qué fuente obtener la información
  Para responder cada pregunta con el mecanismo adecuado (SQL, RAG o ambos)

  Antecedentes:
    Dado que la base de datos contiene partidas, jugadores, aperturas y torneos
    Y que el repositorio RAG contiene las Leyes FIDE y un texto de teoría de aperturas

  Escenario: Pregunta sobre datos estructurados se enruta a SQL
    Cuando el usuario pregunta "¿cuántas partidas jugó Magnus Carlsen en 2023?"
    Entonces el agente enruta la consulta a SQL
    Y no consulta el repositorio RAG

  Escenario: Pregunta conceptual se enruta a RAG
    Cuando el usuario pregunta "¿qué dice la regla FIDE sobre tocar una pieza?"
    Entonces el agente enruta la consulta a RAG
    Y no genera una consulta SQL

  Escenario: Pregunta mixta se enruta a ambas fuentes
    Cuando el usuario pregunta "¿cuántas veces se jugó la Siciliana y cuál es su idea principal?"
    Entonces el agente enruta la consulta a AMBAS
    Y combina el resultado de SQL con el contexto de RAG en la respuesta

  Escenario: Pregunta en inglés se enruta correctamente
    Cuando el usuario pregunta "how many games did Carlsen win with white?"
    Entonces el agente enruta la consulta a SQL
    Y responde en inglés
