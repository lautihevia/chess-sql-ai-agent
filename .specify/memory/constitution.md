<!--
Sync Impact Report (temporal — puede eliminarse antes del commit)
- Versión: (inicial) → 1.0.0
- Principios definidos: I. Grounding-first; II. Seguridad y solo lectura;
  III. Verificabilidad (test-first); IV. Observabilidad; V. Reproducibilidad y documentación;
  VI. Simplicidad (YAGNI)
- Secciones añadidas: Restricciones tecnológicas; Flujo de desarrollo (SDD); Governance
- TODOs diferidos: ninguno
-->

# Constitución de chess-sql-ai-agent

## Principios fundamentales

### I. Grounding-first (cero alucinación)
Toda respuesta DEBE apoyarse en evidencia verificable: el resultado de una consulta SQL real
o un fragmento recuperado de los documentos. Si no hay evidencia suficiente, el agente DEBE
rehusarse ("no encontré esa información") en lugar de inventar. Prohibido completar con
conocimiento general del modelo. Racional: es el criterio central de calidad y confianza del
sistema (ver `docs/agent/grounding-policy.md`).

### II. Seguridad y solo lectura
El agente SOLO ejecuta consultas de lectura (`SELECT`). Las escrituras y operaciones
destructivas están prohibidas y se bloquean por defensa en profundidad: rol de BD de solo
lectura, validación del SQL previa a ejecutar y prompt restrictivo. Los secretos NUNCA se
versionan. Racional: el agente ejecuta SQL generado por un LLM sobre datos reales; la
seguridad no puede depender solo del prompt (ver `docs/security.md`).

### III. Verificabilidad (test-first)
El comportamiento esperado se expresa como escenarios Gherkin ANTES de implementar, y cada
nodo del agente DEBE tener pruebas unitarias. Los escenarios negativos (rehúso, rechazo de
escritura) son obligatorios. Racional: previene regresiones y demuestra que el agente no
delira (ver `docs/quality/test-strategy.md`).

### IV. Observabilidad
Cada ejecución del agente DEBE ser trazable e inspeccionable paso a paso (ruta elegida, SQL
generado, fragmentos recuperados, respuesta, costo) mediante LangSmith. Racional: sin
observabilidad no se puede depurar ni evaluar la calidad (ver `docs/quality/evaluation.md`).

### V. Reproducibilidad y documentación
El proyecto DEBE poder levantarse en un entorno limpio siguiendo el README (esquema + seed
con semilla fija + dependencias). Toda decisión relevante se registra como ADR. Racional: es
requisito del enunciado y condición del trabajo científico/ingenieril.

### VI. Simplicidad (YAGNI)
Ante cada elección se toma la opción más simple que cumple los criterios; no se agrega
complejidad especulativa. Un agente que funciona vale más que documentación perfecta de uno
que no. Racional: el proyecto es individual y acotado en el tiempo (ver `docs/risks.md`, R1).

## Restricciones tecnológicas

Stack fijado (ver `docs/architecture/tech-stack.md` y los ADR en `docs/decisions/`):
Python; Claude API (razonamiento); sentence-transformers (embeddings locales, multilingüe);
PostgreSQL en Supabase con pgvector; LangGraph (orquestación); Streamlit + Streamlit Community
Cloud (UI y despliegue); LangSmith (observabilidad); GitHub Spec Kit (SDD).
Este stack cubre los cinco criterios de promoción del enunciado.

## Flujo de desarrollo (SDD)

- El desarrollo sigue Spec-Driven Development: `constitution → spec → plan → tasks → implement`.
- La documentación de contexto (`docs/`) es la fuente de verdad y precede al código.
- La documentación se escribe en español; los mensajes de commit, en inglés.
- Los commits NO incluyen co-author ni atribución de IA.
- Cada tanda de trabajo se revisa antes de commitear.

## Gobernanza

Esta constitución prevalece sobre otras prácticas del proyecto. Las enmiendas se documentan en
este archivo, con versionado semántico (MAJOR: cambios incompatibles de principios; MINOR:
nuevo principio o guía ampliada; PATCH: aclaraciones). Todo cambio de código DEBE ser
consistente con estos principios; las excepciones se justifican explícitamente. Para guía de
desarrollo en tiempo de ejecución se usan los documentos en `docs/`.

**Versión**: 1.0.0 | **Ratificada**: 2026-09-26 | **Última enmienda**: 2026-09-26
