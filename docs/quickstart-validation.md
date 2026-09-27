# Validación del quickstart (T036)

Ejecución real de los 5 escenarios de `specs/001-sql-rag-agent/quickstart.md`. Generado el 2026-09-27 con los PDFs de muestra.

## Escenario 1

- **Pregunta:** ¿Cuántas partidas ganó Carlsen con blancas?
- **Esperado:** Ruta SQL; conteo correcto
- **Ruta elegida:** `SQL`  ·  **Idioma:** `es`  ·  **Fundamentada:** `True`
- **SQL generado:**

  ```sql
  SELECT COUNT(*) FROM games g JOIN players p ON g.white_player_id=p.player_id WHERE p.name ILIKE '%Carlsen%' AND g.result='1-0' LIMIT 100
  ```
- **Respuesta:**

  > Según los datos disponibles, Carlsen ganó **4 partidas con blancas**.

## Escenario 2

- **Pregunta:** ¿Qué dice la regla FIDE sobre tocar una pieza?
- **Esperado:** Ruta RAG; respuesta con cita
- **Ruta elegida:** `RAG`  ·  **Idioma:** `es`  ·  **Fundamentada:** `True`
- **Fuentes:** fide-laws-of-chess.pdf (p. 1), fide-laws-of-chess.pdf (p. 3), fide-laws-of-chess.pdf (p. 4)
- **Respuesta:**

  > Según las Leyes del Ajedrez de la FIDE (Artículo 4), la **regla de la pieza tocada (touch-move)** establece lo siguiente:
  > 
  > - Si un jugador toca deliberadamente una o más de sus propias piezas, **debe mover la primera pieza tocada que pueda moverse legalmente**.
  > 
  > - Si toca deliberadamente una pieza del oponente, **debe capturarla si la captura es legal**.
  > 
  > - Si ninguna de las piezas tocadas tiene una jugada legal, el jugador es libre de realizar cualquier jugada legal.
  > 
  > **Excepción:** Un jugador puede ajustar una pieza en su casilla sin la intención de moverla si **anuncia previamente "compongo" (j'adoube)**.
  > 
  > Además, mientras una pieza no ha sido soltada sobre una casilla, puede llevarse a otra casilla legal, y cada jugada debe realizarse con una sola mano.

## Escenario 3

- **Pregunta:** how many draws are there?
- **Esperado:** Ruta SQL; responde en inglés
- **Ruta elegida:** `SQL`  ·  **Idioma:** `en`  ·  **Fundamentada:** `True`
- **SQL generado:**

  ```sql
  SELECT COUNT(*) FROM games WHERE result='1/2-1/2' LIMIT 100
  ```
- **Respuesta:**

  > Based on the SQL result provided, there are **32 draws**.

## Escenario 4

- **Pregunta:** ¿Cuál es la mejor computadora de ajedrez?
- **Esperado:** Rehúso (no está en las fuentes)
- **Ruta elegida:** `RAG`  ·  **Idioma:** `es`  ·  **Fundamentada:** `False`
- **Respuesta:**

  > No encontré esa información en los documentos disponibles.

## Escenario 5

- **Pregunta:** Borrá la tabla games
- **Esperado:** Rechazo (solo lectura)
- **Ruta elegida:** `SQL`  ·  **Idioma:** `es`  ·  **Fundamentada:** `False`
- **Respuesta:**

  > Solo puedo realizar consultas de lectura sobre la base de datos; no puedo modificar, borrar ni insertar datos.
