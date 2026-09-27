# Contexto de producto

## Problema

Consultar información sobre partidas de ajedrez requiere, hoy, dos habilidades distintas:
saber **SQL** para interrogar datos estructurados (jugadores, resultados, aperturas,
torneos) y **buscar manualmente** en reglamentos o libros de teoría cuando la pregunta es
conceptual (reglas, ideas estratégicas). Un usuario no técnico no puede hacer ninguna de
las dos con fluidez.

## Solución

Un agente de IA que recibe preguntas en **lenguaje natural** (castellano o inglés) y
**decide solo** de qué fuente obtener la respuesta:

- **Datos estructurados** → traduce la pregunta a SQL, la ejecuta contra la base y devuelve
  el resultado (ej. *"¿cuántas partidas ganó Carlsen con blancas?"*).
- **Conocimiento textual** → recupera fragmentos relevantes de documentos PDF mediante RAG
  y responde citando la fuente (ej. *"¿qué dice la regla FIDE sobre tocar una pieza?"*).

## Usuarios

- **Usuario final**: aficionado/estudiante de ajedrez que quiere respuestas rápidas sin
  saber SQL ni leer reglamentos completos.
- **Evaluador (cátedra)**: verifica que el agente enrute e interprete correctamente ambas
  fuentes.

## Valor

- Una única interfaz conversacional para dos tipos de conocimiento (estructurado + textual).
- Respuestas **fundamentadas** (SQL real o cita de documento), no inventadas.
- Trazabilidad: se puede auditar qué decidió el agente en cada paso.

## Motivación académica (contexto del TP)

Trabajo Práctico Integrador de **AI Engineering** (Ingeniería en Informática, 5to año). El
objetivo pedagógico es integrar, en un sistema funcional, las técnicas centrales de la
ingeniería de aplicaciones con LLMs: **text-to-SQL**, **RAG**, **orquestación de agentes**,
**observabilidad** y **despliegue**. Se apunta a **promoción directa**, cubriendo los cinco
criterios opcionales del enunciado. Ver [alcance y límites](../architecture/system-boundary.md).
