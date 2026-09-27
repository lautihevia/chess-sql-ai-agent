# ADR 0005 — Vector store con pgvector en Supabase

- **Estado:** aceptada
- **Fecha:** 2026-09-26

## Contexto

Los vectores del RAG necesitan un almacén con búsqueda por similitud. Ya usamos Supabase para
la base relacional y queremos que el RAG también quede **en la nube** (refuerza el criterio de
despliegue).

## Decisión

Usar **pgvector dentro de Supabase**, unificando datos relacionales y vectores en una sola
base en la nube.

## Alternativas consideradas

- **Chroma local (archivo):** más simple de arrancar, pero queda fuera de la nube y agrega un
  segundo almacenamiento a gestionar.

## Consecuencias

- (+) Todo en una sola BD en la nube; menos piezas móviles; refuerza el criterio de nube.
- (−) Un poco más de setup (habilitar la extensión, crear la tabla de vectores).
- **Plan B:** si pgvector diera problemas, se usa **Chroma local** sin cambiar el resto del
  diseño (el nodo RAG abstrae el almacén). Ver [risks.md](../risks.md) (R5).
