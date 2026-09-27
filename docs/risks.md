# Riesgos y mitigaciones

Riesgos del proyecto (contexto: individual, ~3 semanas, principiante en Python/IA) y cómo se
mitigan. Fecha de entrega: **16/10/2026**.

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | **Tiempo insuficiente** por hacerlo solo y aprender la stack | Alta | Alto | Priorizar lo que aprueba/promociona; usar servicios gratuitos y managed; cortar el "gold-plating" de docs y avanzar al código |
| R2 | Curva de **Python/LLM/RAG** siendo principiante | Media | Alto | Andamiaje paso a paso; empezar por un flujo mínimo end-to-end y luego iterar |
| R3 | El LLM genera **SQL incorrecto** (columnas/valores inventados) | Media | Medio | Diccionario de datos + term-mapping + few-shot en el prompt; reintento con el error; validación |
| R4 | **Alucinaciones** en RAG | Media | Medio | Política de grounding; citar fuente; rehúso cuando no hay evidencia; evaluación en LangSmith |
| R5 | Setup de **pgvector** en Supabase más complejo de lo esperado | Media | Medio | Plan B: Chroma local para el vector store (ver [ADR 0005](decisions/0005-pgvector.md)) |
| R6 | **Costos** de API de Claude | Baja | Bajo | Modelo económico para routing/SQL; monitoreo de tokens en LangSmith |
| R7 | Problemas de **despliegue** (Streamlit Cloud + Supabase + secrets) | Media | Medio | Probar el deploy temprano con un "hola mundo"; documentar secrets en deployment.md |
| R8 | **Datos sintéticos** poco realistas → consultas triviales | Baja | Bajo | Estrategia de seed con distribución variada y verificación contra golden queries |
| R9 | Alcance de **SDD** (Spec Kit) desvía tiempo del producto | Media | Bajo | Usar Spec Kit de forma acotada; los docs ya cubren gran parte del input |

## Riesgo principal

**R1 (tiempo)** es el que más vigilar. Estrategia: tener cuanto antes un agente mínimo
funcionando end-to-end (una pregunta SQL + una RAG) y recién después pulir. Un agente que
anda vale más que documentación perfecta de uno que no.
