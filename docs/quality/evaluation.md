# Evaluación del agente

Cómo se mide, de forma **sistemática y medible**, que el agente responde bien (y no delira).
Cubre el criterio de promoción **observabilidad y evaluación** usando **LangSmith**.

## Dataset de evaluación

Conjunto curado de casos `pregunta → resultado esperado`, construido a partir de:

- Las [golden queries](../agent/golden-queries.md) (ruta SQL).
- Preguntas de reglas/ideas cubiertas por los PDFs (ruta RAG).
- **Casos de rehúso** (preguntas sin datos / fuera de los documentos), para medir que el
  agente dice "no sé" en vez de inventar.
- Preguntas equivalentes en **español e inglés**.

Cada caso incluye: la pregunta, la ruta esperada, y el resultado/afirmación esperada (o
"debe rehusar").

## Métricas

| Métrica | Qué mide |
|---|---|
| **Exactitud de enrutamiento** | % de preguntas enviadas a la ruta correcta (SQL/RAG/AMBAS) |
| **Exactitud SQL** | % de respuestas SQL cuyo resultado coincide con el esperado |
| **Fidelidad RAG (groundedness)** | % de respuestas RAG apoyadas en los fragmentos, con cita |
| **Tasa de rehúso correcto** | % de casos sin evidencia en los que el agente rehúsa correctamente |
| **Latencia y costo** | Tiempo y tokens por consulta (desde las trazas) |

## Método

1. Cargar el dataset en LangSmith.
2. Correr el agente sobre todo el dataset (experimento).
3. Evaluar con verificadores automáticos (comparación de resultado SQL, chequeo de cita/
   groundedness) y, donde haga falta, un evaluador LLM-as-judge.
4. Registrar resultados por versión del agente para comparar mejoras.

## Evidencia para el informe

- Tabla de métricas por ruta.
- Capturas de trazas de LangSmith (ejemplos correctos y de rehúso).
- Comparación antes/después de algún ajuste de prompt.

Relación con las pruebas de código: ver [test-strategy.md](test-strategy.md).
