# Vista de contenedores (C4 nivel 2)

Detalle de los componentes internos del sistema y cómo se comunican.

```mermaid
graph TB
    user([👤 Usuario])

    subgraph app["chess-sql-ai-agent"]
        ui[Interfaz Streamlit<br/>chat + panel de trazabilidad]

        subgraph agent["Agente LangGraph"]
            router[Nodo Router<br/>clasifica: SQL / RAG / AMBAS]
            sqlnode[Nodo SQL<br/>text-to-SQL + validación + ejecución]
            ragnode[Nodo RAG<br/>embed pregunta + búsqueda + contexto]
            synth[Nodo Síntesis<br/>redacta respuesta final]
        end

        emb[Embeddings<br/>sentence-transformers]
        ingest[Pipeline de indexado<br/>PDF → chunks → vectores]
    end

    db[(Supabase<br/>tablas relacionales)]
    vec[(Supabase<br/>pgvector)]
    claude[Claude API]
    langsmith[LangSmith]
    pdfs[[PDFs]]

    user --> ui --> router
    router --> sqlnode
    router --> ragnode
    sqlnode --> synth
    ragnode --> synth
    synth --> ui

    sqlnode -->|SELECT| db
    sqlnode -.->|genera SQL| claude
    router -.->|clasifica| claude
    synth -.->|redacta| claude
    ragnode --> emb
    ragnode -->|similitud| vec
    ingest --> emb
    ingest --> vec
    pdfs -.-> ingest
    agent -.->|trazas| langsmith
```

## Componentes

| Componente | Responsabilidad | Depende de |
|---|---|---|
| **Interfaz Streamlit** | Entrada/salida con el usuario; muestra respuesta, SQL y fuentes | Agente |
| **Nodo Router** | Clasifica la pregunta en SQL / RAG / AMBAS | Claude |
| **Nodo SQL** | Genera SQL, lo valida (solo lectura), lo ejecuta y captura el resultado | Claude, Supabase (tablas) |
| **Nodo RAG** | Convierte la pregunta en vector, busca fragmentos y arma el contexto | Embeddings, Supabase (pgvector) |
| **Nodo Síntesis** | Redacta la respuesta final citando lo que corresponda | Claude |
| **Embeddings** | Vectoriza texto (multilingüe), en local | — |
| **Pipeline de indexado** | Proceso offline: PDFs → chunks → vectores en pgvector | Embeddings, Supabase |

Cada nodo es una **unidad testeable por separado** (ver [test-strategy.md](../quality/test-strategy.md)).
El flujo detallado del grafo está en [agent-flow.md](../agent/agent-flow.md).
