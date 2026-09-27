# Contratos de interfaces (Fase 1)

Interfaces que expone el sistema. Como es una aplicación con agente (no una API pública), los
contratos relevantes son el de **consulta al agente** y el de **seguridad del nodo SQL**.

## Contrato 1 — Consulta al agente

**Entrada**:
```
{
  "pregunta": "texto en lenguaje natural (es|en)"
}
```

**Salida**:
```
{
  "respuesta": "texto en el idioma de la pregunta",
  "ruta": "SQL | RAG | AMBAS",
  "sql_generado": "string | null",      # si hubo ruta SQL
  "fuentes": ["documento / referencia", ...],  # si hubo ruta RAG
  "fundamentada": true | false           # false ⇒ rehúso explícito
}
```

**Reglas**:
- Si no hay evidencia suficiente, `fundamentada = false` y `respuesta` es un rehúso honesto
  (Principio I).
- La respuesta va siempre en el idioma de la pregunta (RF-008).

## Contrato 2 — Seguridad del nodo SQL

**Precondición**: el SQL generado se valida **antes** de ejecutarse.

**Invariantes**:
- Solo se acepta una sentencia `SELECT`. Cualquier `INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE`,
  múltiples sentencias o comandos peligrosos → **rechazo** (RF-007, Principio II).
- Se agrega un `LIMIT` máximo si la consulta no lo tiene.
- La conexión usa un rol de BD de **solo lectura** (defensa en profundidad).

**Salida ante violación**: no se ejecuta nada; el agente responde que solo puede consultar datos.

## Contrato 3 — Recuperación RAG

**Entrada**: pregunta (texto). **Salida**: lista de fragmentos con su metadata (fuente, página).

**Regla**: si ningún fragmento supera el umbral de relevancia, se devuelve lista vacía y el agente
rehúsa (no inventa).

> Estos contratos se verifican con los escenarios de
> [`docs/requirements/use-cases/`](../../docs/requirements/use-cases/) y las pruebas de
> [`docs/quality/test-strategy.md`](../../docs/quality/test-strategy.md).
