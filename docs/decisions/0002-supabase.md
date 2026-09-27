# ADR 0002 — Base de datos en Supabase

- **Estado:** aceptada
- **Fecha:** 2026-09-26

## Contexto

Se necesita una base relacional que además esté **en la nube** (criterio de promoción). El
desarrollador conoce bases de datos pero es principiante en el resto de la stack.

## Decisión

Usar **PostgreSQL administrado en Supabase** (free tier).

## Alternativas consideradas

- **Neon:** Postgres en la nube, free tier, muy liviano; válido.
- **SQLite local:** lo más simple, pero **no** cumple "BD en la nube".

## Consecuencias

- (+) Cumple el criterio de BD en la nube; free tier sin tarjeta.
- (+) Editor de tablas visual (cómodo y útil para el coloquio).
- (+) Trae **pgvector**, que permite unificar datos y vectores (ver [ADR 0005](0005-pgvector.md)).
- (−) Dependencia de un servicio externo (se mitiga con esquema + seed reproducibles).
