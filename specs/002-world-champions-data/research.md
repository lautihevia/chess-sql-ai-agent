# Investigación y decisiones (Fase 0)

Registro de lo que se investigó y por qué se decidió cada cosa. Es retroactivo: documenta el
proceso real, incluidos los errores que se corrigieron por el camino.

## 1. ¿Qué PDFs cargar?

- **Decisión**: tres exportaciones de Wikipedia a PDF (lista de campeonatos mundiales, historia
  general en inglés, versión en español). **Fuente**: `https://<idioma>.wikipedia.org/api/rest_v1/page/pdf/<Título>`.
- **Alternativas descartadas**: el artículo del match de 2024 (ya cubierto por la historia general)
  y la línea de tiempo del World Chess Hall of Fame (21 páginas, 9,6 MB, sin llegar al campeón
  actual). No se encontraron PDFs "nativos" con la lista de campeones.
- **Licencia**: CC BY-SA; hay que citar la fuente.

## 2. ¿Por qué tablas SQL si ya hay PDFs?

- **Hallazgo**: preguntas como "¿quién fue campeón en 1972?" no recuperaban el fragmento correcto.
  Al extraer el texto, cada fila de la tabla queda repartida en varias líneas
  (`1972 | Reykjavík | Bobby | Fischer 12½ – 8½ | Boris | Spassky`) y el embedding no distingue
  bien entre años.
- **Decisión**: los hechos con respuesta exacta se cargan como tablas; el RAG queda para el contexto.

## 3. Relación con `players`

- **Hallazgo**: `players` tiene 30 personas (20 reales, 10 sintéticas) que se usan para generar
  partidas sintéticas; solo 8 campeones están ahí.
- **Alternativas**: (a) agregar a los campeones históricos a `players` — descartada: habría que
  inventarles rating y país, y jugarían partidas de 2023; (b) dos columnas opcionales en
  `world_championships` — descartada: relación a medias.
- **Decisión**: tabla `champions` propia, con vínculo opcional a `players`.

## 4. Clave del vínculo `champions` ↔ `players`

- **Primer intento**: comparar nombres. Descartado en la revisión: no hay estándar de nombres
  ("Gukesh D" en Wikidata y la FIDE, "Gukesh Dommaraju" en el PDF) ni validación.
- **Segundo intento**: id de Wikidata. Descartado en la revisión: es un identificador de una
  fuente externa, no del dominio.
- **Decisión**: FIDE ID. Wikidata (P1440) lo tiene para 20 de 20 jugadores reales y 25 de 44
  campeones; se contrastó con la ficha de cada uno en `ratings.fide.com`: coinciden 33 de 37
  (los otros 4 —Firouzja, Spassky, Timman y Korchnoi— no se pudieron confirmar y quedan sin id).
  Los 19 campeones históricos no tienen FIDE ID en Wikidata.

## 5. País de los campeones

- **Hallazgo**: Wikidata trae varias nacionalidades por persona, con cambios históricos
  (Alekhine: Francia, Imperio ruso, URSS...), y "país deportivo" contradictorio (Capablanca:
  "Spain"; Kamsky: "France"; Khalifman: "FIDE").
- **Decisión**: no guardar el país; elegir uno sería un juicio, no un dato.
- **Idea pendiente**: la tabla de la página 10 del PDF en español lista, por campeón, años de
  reinado, país y edad, con una fuente propia.

## 6. Tamaño de los chunks

- **Hallazgo**: `paraphrase-multilingual-MiniLM-L12-v2` solo lee 128 tokens; el 91% de los chunks de
  250 palabras los superaba, y la información del medio no se podía recuperar.
- **Decisión**: 70 palabras, solape 15 y `k = 8`. Mediciones y alternativas completas en el
  [ADR 0006](../../docs/decisions/0006-tamano-de-chunk-y-k.md).

## 7. Limitaciones conocidas

- Las preguntas en español sobre documentos en inglés recuperan peor ("rey ahogado" no encuentra
  *stalemate*; la sigla "PCA" sola recupera poco). Mejora propuesta: traducir la pregunta antes de
  recuperar.
- El nodo de síntesis es conservador: si la evidencia no responde literalmente, rehúsa. Se vio con
  "¿contra quién jugó Anand su primer match?" hasta que se nombró la columna `first_title_match_year`.
- "Campeón en el año X" devuelve el último match anterior, pero el año que acompaña es el del
  último match, no el de la coronación.
- El match de 2026 (Gukesh vs. Sindarov) figura en el PDF sin resultado y no se carga.
