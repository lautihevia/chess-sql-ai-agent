# Golden queries (catálogo de referencia)

Pares curados **pregunta en lenguaje natural → SQL correcto**. Cumplen doble función:

1. **Few-shot**: se incluyen como ejemplos en el prompt del nodo SQL para guiar al LLM.
2. **Evaluación**: forman parte del dataset con el que se mide la precisión en LangSmith
   (ver [evaluation.md](../quality/evaluation.md)).

> El SQL asume el esquema del [diccionario de datos](../data/data-dictionary.md).
> Se muestran sin `LIMIT` por claridad; en ejecución el nodo agrega un límite de seguridad.

| # | Pregunta | SQL esperado |
|---|---|---|
| 1 | ¿Cuántas partidas ganó Magnus Carlsen con blancas? | `SELECT COUNT(*) FROM games g JOIN players p ON g.white_player_id=p.player_id WHERE p.name='Magnus Carlsen' AND g.result='1-0';` |
| 2 | ¿Cuántas partidas ganó Carlsen en total? | `SELECT COUNT(*) FROM games g JOIN players p ON p.player_id IN (g.white_player_id,g.black_player_id) WHERE p.name='Magnus Carlsen' AND ((g.white_player_id=p.player_id AND g.result='1-0') OR (g.black_player_id=p.player_id AND g.result='0-1'));` |
| 3 | Top 5 jugadores por peak rating | `SELECT name, peak_rating FROM players ORDER BY peak_rating DESC NULLS LAST LIMIT 5;` |
| 4 | ¿Cuál fue la apertura más jugada en el Tata Steel 2023? | `SELECT o.name, COUNT(*) c FROM games g JOIN openings o ON g.opening_id=o.opening_id JOIN tournaments t ON g.tournament_id=t.tournament_id WHERE t.name='Tata Steel 2023' GROUP BY o.name ORDER BY c DESC LIMIT 1;` |
| 5 | Rating promedio de los jugadores de Noruega | `SELECT AVG(peak_rating) FROM players WHERE country='Norway';` |
| 6 | ¿Cuántas partidas terminaron en tablas? | `SELECT COUNT(*) FROM games WHERE result='1/2-1/2';` |
| 7 | ¿Qué jugadores tienen título de Gran Maestro? | `SELECT name FROM players WHERE title='GM';` |
| 8 | ¿Cuántos torneos hay por país? | `SELECT country, COUNT(*) FROM tournaments GROUP BY country ORDER BY COUNT(*) DESC;` |
| 9 | ¿Cuál es la partida con más movimientos? | `SELECT game_id, num_moves FROM games ORDER BY num_moves DESC LIMIT 1;` |
| 10 | ¿Cuántas veces se jugó la Defensa Siciliana? | `SELECT COUNT(*) FROM games g JOIN openings o ON g.opening_id=o.opening_id WHERE o.name ILIKE '%Sicilian%';` |
| 11 | Evolución del rating de Carlsen | `SELECT r.rating_date, r.rating FROM player_ratings r JOIN players p ON r.player_id=p.player_id WHERE p.name='Magnus Carlsen' ORDER BY r.rating_date;` |
| 12 | ¿Cuántas partidas jugó cada jugador? | `SELECT p.name, COUNT(*) FROM games g JOIN players p ON p.player_id IN (g.white_player_id,g.black_player_id) GROUP BY p.name ORDER BY COUNT(*) DESC;` |
| 13 | ¿En qué torneos jugó Carlsen? | `SELECT DISTINCT t.name FROM games g JOIN tournaments t ON g.tournament_id=t.tournament_id JOIN players p ON p.player_id IN (g.white_player_id,g.black_player_id) WHERE p.name='Magnus Carlsen';` |
| 14 | ¿Cuál es el jugador más joven? | `SELECT name, birth_year FROM players WHERE birth_year IS NOT NULL ORDER BY birth_year DESC LIMIT 1;` |
| 15 | ¿Cuántas partidas ganaron las blancas vs las negras? | `SELECT result, COUNT(*) FROM games WHERE result IN ('1-0','0-1') GROUP BY result;` |

Se ampliará el catálogo a ~20 pares durante la implementación, cubriendo también casos de
rehúso (preguntas sin datos) para robustecer la evaluación.
