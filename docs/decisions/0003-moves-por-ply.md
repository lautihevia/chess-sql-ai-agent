# ADR 0003 — Modelado de `moves`: una fila por media jugada (ply)

- **Estado:** aceptada
- **Fecha:** 2026-09-26

## Contexto

Hay que decidir cómo guardar las jugadas de cada partida. Preocupación planteada: que las
consultas sobre una partida resulten pesadas si hay muchas filas.

## Decisión

Guardar **una fila por media jugada (ply)** en la tabla `moves`, con un **índice en
`game_id`**.

## Alternativas consideradas

- **Partida como texto (PGN) en `games`:** una fila por partida, más simple, pero se pierde la
  capacidad de consultar jugadas por SQL y quedaríamos en 5 tablas justas.

## Consecuencias

- (+) Habilita consultas a nivel jugada (ej. "primera jugada más común").
- (+) Modelo normalizado, prolijo para el informe.
- (+) Rendimiento no es problema: a este volumen (~miles de filas), con índice en `game_id`,
  reconstruir una partida es instantáneo.
- (−) Más filas y un `seed` algo más elaborado (aceptable).
