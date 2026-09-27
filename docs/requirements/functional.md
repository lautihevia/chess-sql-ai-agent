# Requisitos funcionales

Qué **debe hacer** el sistema. Cada requisito tiene un criterio de aceptación verificable;
muchos se validan con los escenarios Gherkin de [`use-cases/`](use-cases/).

| ID | Requisito | Criterio de aceptación |
|---|---|---|
| **RF-01** | Recibir preguntas en lenguaje natural en **español o inglés** | El agente responde correctamente a preguntas equivalentes en ambos idiomas |
| **RF-02** | **Enrutar** la pregunta a la fuente adecuada: `SQL`, `RAG` o `AMBAS` | Ante una pregunta de datos elige SQL; ante una conceptual, RAG; ante una mixta, ambas |
| **RF-03** | Generar **SQL válido** a partir del esquema para preguntas de datos | El SQL ejecuta sin error y usa columnas/valores reales del [diccionario](../data/data-dictionary.md) |
| **RF-04** | **Ejecutar** el SQL contra PostgreSQL y obtener el resultado | El resultado devuelto coincide con el de la consulta ejecutada manualmente |
| **RF-05** | **Recuperar** fragmentos relevantes de los PDFs (RAG) para preguntas conceptuales | Los fragmentos recuperados contienen la información necesaria para responder |
| **RF-06** | **Citar la fuente** (documento y, si aplica, sección/página) en respuestas RAG | La respuesta incluye una referencia a la fuente usada |
| **RF-07** | **Sintetizar** una respuesta final en lenguaje natural, en el idioma de la pregunta | La respuesta es correcta, clara y en el mismo idioma que la consulta |
| **RF-08** | Manejar el caso **AMBAS**: combinar resultado SQL + contexto RAG en una sola respuesta | La respuesta integra dato estructurado y conocimiento textual de forma coherente |
| **RF-09** | **Reintentar** una vez ante SQL fallido, pasándole el error al LLM para que lo corrija | Un error corregible (ej. columna mal nombrada) se resuelve en el reintento |
| **RF-10** | **Rehusar con fundamento** cuando no hay evidencia (ni datos ni documentos) | Responde "no encontré esa información" en vez de inventar |
| **RF-11** | Ofrecer una **interfaz de chat** (Streamlit) que muestre la respuesta y, opcionalmente, el SQL generado y las fuentes | El usuario puede preguntar y ver respuesta + trazabilidad en la UI |
| **RF-12** | **Registrar la traza** de cada consulta (ruta, SQL/fragmentos, respuesta) en LangSmith | Cada consulta genera una traza inspeccionable |

Ver también: [requisitos no funcionales](non-functional.md) y [política de grounding](../agent/grounding-policy.md).
