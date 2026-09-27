# Esqueleto del informe técnico

Estructura propuesta para el informe (**máx. 10 páginas**) que pide el enunciado. Cada sección
**reutiliza** documentación ya escrita, así redactarlo es en gran parte ensamblar y resumir.

| Sección | Contenido | Fuente (docs) | Págs aprox. |
|---|---|---|---|
| 1. Introducción | Objetivo del TP, problema y solución en breve | [product-context](context/product-context.md) | 0.5 |
| 2. Modelo de datos | Las 6 tablas, diagrama ER, decisiones de modelado | [data-model](data/data-model.md), [data-dictionary](data/data-dictionary.md) | 1.5 |
| 3. Arquitectura del agente | Grafo LangGraph, nodos, routing SQL/RAG, RAG | [agent-flow](agent/agent-flow.md), [container-view](architecture/container-view.md) | 2 |
| 4. Decisiones técnicas | Stack y por qué; resumen de ADRs | [tech-stack](architecture/tech-stack.md), [decisions/](decisions/) | 1.5 |
| 5. Anti-alucinación y seguridad | Grounding, guardrails SQL, inyección | [grounding-policy](agent/grounding-policy.md), [security](security.md) | 1 |
| 6. Ejemplos de consultas | Preguntas NL → respuesta (SQL y RAG), capturas | [golden-queries](agent/golden-queries.md) | 1 |
| 7. Pruebas y evaluación | Estrategia de pruebas + métricas de LangSmith | [test-strategy](quality/test-strategy.md), [evaluation](quality/evaluation.md) | 1.5 |
| 8. Despliegue | App + BD en la nube; reproducibilidad | [deployment](architecture/deployment.md) | 0.5 |
| 9. Conclusiones | Qué se logró, criterios de promoción cubiertos, mejoras futuras | [tech-stack](architecture/tech-stack.md) (criterios) | 0.5 |

## Evidencias a incluir (enunciado)

- Diagrama del modelo de datos (ER).
- Diagrama de la arquitectura del agente.
- Ejemplos de consultas realizadas (capturas de la app).
- Evidencias de funcionamiento: capturas y **trazas de LangSmith**, resultados de la evaluación.

## Checklist de entregables

- [ ] Repositorio con código fuente completo.
- [ ] Datos empleados: base de datos + PDFs.
- [ ] README con instrucciones de instalación y ejecución.
- [ ] Informe técnico (≤10 págs).
- [ ] Artefactos de SDD (Spec Kit).
