# ADR 0001 — Orquestación con LangGraph

- **Estado:** aceptada
- **Fecha:** 2026-09-26

## Contexto

El agente debe **decidir** entre consultar la base (SQL) o los documentos (RAG), y a veces
ambas. Necesitamos un mecanismo de orquestación claro, trazable y defendible en el coloquio,
sabiendo que el desarrollador es principiante en la stack.

## Decisión

Usar **LangGraph** con un **router explícito** y nodos separados (router, SQL, RAG, síntesis).

## Alternativas consideradas

- **Agente ReAct con tools (LangChain):** menos código, pero más "caja negra" y trazas caóticas.
- **Routing manual (if/clasificador):** lo más simple, pero **no cumple** el criterio de
  promoción de "framework agéntico".

## Consecuencias

- (+) Cumple el criterio de framework agéntico; flujo explícito y didáctico; trazas limpias
  en LangSmith; excelente para la defensa oral.
- (+) Cada nodo es una unidad testeable por separado.
- (−) Algo más de código que un agente "mágico" (aceptable, y mejor para aprender).
