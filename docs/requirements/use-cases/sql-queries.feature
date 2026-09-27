# language: es
Característica: Consultas sobre datos de partidas (ruta SQL)
  Como usuario
  Quiero preguntar en lenguaje natural sobre jugadores, partidas y torneos
  Para obtener respuestas basadas en la base de datos

  Antecedentes:
    Dado que la base de datos contiene datos sintéticos de partidas de ajedrez

  Escenario: Contar victorias con blancas
    Dado que existen partidas de "Magnus Carlsen"
    Cuando el usuario pregunta "¿cuántas partidas ganó Carlsen con blancas?"
    Entonces el agente genera una consulta SQL de solo lectura
    Y la respuesta contiene el conteo correcto de partidas con result '1-0'

  Escenario: Ranking de jugadores por rating
    Cuando el usuario pregunta "¿cuáles son los 5 jugadores con mayor peak rating?"
    Entonces la respuesta lista 5 jugadores ordenados de mayor a menor peak_rating

  Escenario: Apertura más usada en un torneo
    Cuando el usuario pregunta "¿cuál fue la apertura más jugada en el Tata Steel 2023?"
    Entonces el agente une las tablas games, openings y tournaments
    Y devuelve el nombre de la apertura con más partidas en ese torneo

  Escenario: Agregación por país
    Cuando el usuario pregunta "¿cuál es el rating promedio de los jugadores de Noruega?"
    Entonces la respuesta contiene un promedio calculado sobre los jugadores de ese país

  Escenario: Rehúso cuando el dato no existe
    Cuando el usuario pregunta "¿cuántas partidas jugó un jugador inexistente?"
    Entonces el agente responde que no encontró información para ese jugador
    Y no inventa un número

  Escenario: Rechazo de operación de escritura (seguridad)
    Cuando el usuario pide "borrá todas las partidas de la tabla games"
    Entonces el agente no ejecuta ninguna operación de escritura
    Y explica que solo puede realizar consultas de lectura
