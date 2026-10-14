# Guía de validación (quickstart)

Cómo reproducir y verificar la funcionalidad de punta a punta.

## Prerrequisitos

- `.env` completo (ver README) y dependencias instaladas con `uv sync`.
- La base de Supabase con las tablas base ya cargadas (`uv run python -m chess_agent.db.seed`).

## 1. Cargar los campeonatos

```bash
# Solo las tablas champions y world_championships (no toca el resto de la base):
uv run python -m chess_agent.db.championships
# -> champions: 44 filas | world_championships: 58 filas
```

En una base nueva, `uv run python -m chess_agent.db.seed` las carga junto con todo lo demás.

## 2. Indexar los PDFs

```bash
uv run python -m chess_agent.rag.ingest
```

Hay que correrlo de nuevo si se cambia `CHUNK_WORDS`. Resultado esperado (chunks de 70 palabras):
~1.600 chunks entre los 5 PDFs.

## 3. Verificar

```bash
uv run pytest tests/unit                  # integridad de los datos, sin BD ni API
uv run python -m tests.eval.run_eval --local   # 22 casos contra el agente real
```

Métricas de referencia: enrutamiento 100%, SQL 100%, rehúso correcto 100%, fidelidad RAG 62%
(5/8; los 3 fallos están explicados en `research.md` y en el informe).

## 4. Preguntas de prueba

| Pregunta | Ruta | Respuesta esperada |
|---|---|---|
| ¿Quién fue campeón del mundo en 1972 y a quién derrotó? | SQL | Bobby Fischer, a Boris Spassky, 12½–8½ |
| ¿Cuántos títulos mundiales ganó Kasparov? | SQL | 6 |
| ¿Cuántos años vivió Capablanca? | SQL | 54 |
| ¿Quién era campeón del mundo en 1950? | SQL | Mikhail Botvinnik |
| ¿Cuál es el peak rating de los campeones que están en la lista de jugadores? | SQL | Carlsen 2882, Anand y Kramnik 2817, Ding Liren 2816, Gukesh 2794 |
| ¿Por qué perdió Fischer el título en 1975? | RAG | Disputa por el formato del match; Karpov campeón por defecto (con fuente) |
| ¿Cuál fue el reinado más largo de un campeón? | RAG | Lasker, 27 años (1894–1921) |
| ¿Quién ganó el campeonato mundial de 2026? | rehúso | "No encontré información…" |
| ¿Quiénes fueron los campeones soviéticos? | rehúso | "No encontré información…" (no se guarda el país) |
