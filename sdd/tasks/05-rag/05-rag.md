# Tasks - RAG

## Reglas de atomizacion

- Ejecutar estas tareas en orden.
- Mantener RAG dentro de `hydra/backend/`; no tocar frontend.
- No crear ni modificar `.env` reales.
- Versionar solo cambios de codigo, SDD y lockfiles permitidos por cada tarea.
- No llamar modelos reales, embeddings, Langfuse, DB viva ni red externa en verificaciones de tareas `pending` salvo que la tarea lo indique explicitamente.
- Usar fixtures, fakes o servicios inyectados para verificaciones locales.
- No descargar, scrapear, buscar ni inventar documentos reales.
- No versionar documentos reales salvo aprobacion explicita.
- No crear Neo4j ni sinks de grafo en esta mission.
- No cambiar nombres de variables de entorno definidos en SDD.
- No cambiar el contrato de `POST /query` salvo validaciones seguras compatibles.
- No cambiar la dimension de embeddings: debe ser `4096`.
- No crear tablas paralelas que compitan con `documents` o `document_chunks`.
- No marcar tareas como `done` hasta que Codex/reviewer revise diff, comandos y secretos.

## Contexto importante

RAG consume artefactos producidos por misiones anteriores:

- `TASK-DB-011` ya define `document_chunks.embedding vector(4096)`.
- `TASK-CORPUS-024` persiste chunks con `embedding=NULL`.
- `TASK-CORPUS-031` sigue bloqueada hasta tener corpus real aprobado y DB local inicializada.
- La respuesta de `POST /query` debe ajustarse a `sdd/03-api-contract.md`.

Por eso esta carpeta separa:

- codigo RAG verificable con fakes y sin red;
- carga real de embeddings, que queda bloqueada hasta tener corpus/DB/model key;
- smoke tests reales de retrieval/query, tambien bloqueados hasta tener datos y servicios.

## Clarificacion sobre PGVector

En este SDD, `PGVector` significa usar PostgreSQL + la extension `pgvector` sobre la tabla canonica `document_chunks` definida en `sdd/02-data-model.md` y `backend/src/hydra_api/db_schema.py`.

No usar una integracion que cree tablas LangChain paralelas si eso evita `document_chunks`. Si una libreria obliga a crear tablas propias, parar y pedir confirmacion antes de cambiar el modelo de datos.

## Lecciones incorporadas antes de la mission RAG

- Alinear todo SQL con `backend/src/hydra_api/db_schema.py`; no inventar columnas ni nombres de tablas.
- Validar que cada embedding tenga exactamente `4096` dimensiones antes de persistir o consultar.
- Mantener clientes de modelo y conexiones DB lazy; nada de llamadas en import time.
- No aceptar `top_k <= 0` ni preguntas vacias.
- No generar respuestas analiticas si retrieval no devuelve contexto.
- Incluir siempre evidencias o limitaciones.
- No afirmar coordinacion, intencion o atribucion sin evidencia explicita en chunks recuperados.
- No imprimir secretos, headers, stack traces, prompts completos, respuestas completas del modelo ni documentos completos.
- Mantener dry-runs y verificaciones locales sin conexiones externas.
- No resetear `processing_status` ni borrar chunks al anadir embeddings.
- No introducir dependencias nuevas fuera de la tarea que las declara.
- Separar dependencias, embeddings, SQL, retriever, prompt, servicio y endpoint.

## Errores probables a evitar

- Usar embeddings de una dimension distinta a `4096`.
- Insertar embeddings en una tabla distinta a `document_chunks` sin actualizar SDD.
- Usar SQL con f-strings que incluyan pregunta, chunk text o IDs de usuario.
- Abrir DB, crear clientes OpenAI o llamar modelos al importar modulos.
- Invocar proveedores reales desde comandos de verificacion no bloqueados.
- Devolver una respuesta inventada cuando no hay chunks recuperados.
- Exponer contenido completo de documentos como evidencia.
- Confundir distancia coseno con score y devolver valores fuera de rango sin explicar.
- Crear variables de entorno nuevas para `top_k`, modelos o DB.
- Tocar `hydra/frontend/`, Neo4j, observabilidad/evals o docs historicos en esta mission.

## Edge cases obligatorios

- Pregunta vacia o solo espacios debe fallar validacion.
- `top_k` omitido debe usar `5`.
- `top_k <= 0` debe fallar validacion antes de llegar al retriever.
- Corpus/DB sin chunks embebidos debe devolver limitacion, no respuesta inventada.
- Chunks con `embedding=NULL` no deben recuperarse como contexto vectorial.
- Embedding de longitud distinta a `4096` debe fallar antes de persistir o consultar.
- Error de proveedor de modelo no debe filtrar API keys, headers ni stack trace al cliente.
- Evidencia devuelta debe ser fragmento breve, no documento completo.
- Scores deben ser numericos y comparables; si se usa distancia coseno, convertir a score de forma consistente.
- El endpoint debe poder probarse con un servicio fake sin DB ni modelo real.
- Si no hay Langfuse, `trace_id` debe ser un ID local seguro.

## Stop conditions generales

- La tarea requiere cambiar el contrato de `POST /query` en `sdd/03-api-contract.md`.
- La tarea requiere cambiar schemas canonicos, tablas o dimension de embeddings.
- La tarea requiere documentos reales, corpus aprobado, DB viva o claves reales y no esta marcada como `blocked`.
- La tarea requiere llamar un proveedor LLM/embedding o Langfuse en una verificacion local no bloqueada.
- La tarea necesita tocar frontend, Neo4j, `.env` reales, docs historicos o archivos fuera de scope.
- La libreria elegida para PGVector crea tablas paralelas incompatibles con `document_chunks`.
- La verificacion no puede ejecutarse sin datos o servicios que todavia no existen.

## Milestones sugeridos para Droid Missions

| Milestone | Tareas | Objetivo | Debe parar para review |
|---|---|---|---|
| 1 | TASK-RAG-001 a TASK-RAG-003 | Dependencias, constantes y validacion de request | Si cambia env vars o contrato API |
| 2 | TASK-RAG-004 a TASK-RAG-009 | Embeddings e indexacion con fakes | Si llama proveedor real o DB viva en verificacion |
| 3 | TASK-RAG-010 a TASK-RAG-012 | Busqueda vectorial y retriever LCEL | Si crea tablas paralelas o ignora `document_chunks` |
| 4 | TASK-RAG-013 a TASK-RAG-017 | Prompt, servicio y endpoint `/query` | Si responde sin evidencias/limitaciones |
| 5 | TASK-RAG-018 a TASK-RAG-020 | Operaciones reales bloqueadas | Bloqueado hasta corpus, DB y claves reales |

## TASK-RAG-001: Anadir dependencias RAG minimas

Estado: review
Prioridad: must

Objetivo:
Anadir las dependencias necesarias para LCEL, cliente OpenAI compatible y adaptador pgvector sin crear tablas paralelas.

Archivos permitidos:
- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`

Dependencias:
- TASK-BACK-001
- TASK-DB-011

Requisitos:
- Anadir dependencias minimas:
  - `langchain-core`
  - `langchain-openai`
  - `pgvector`
- No anadir `langchain-postgres` en esta tarea si implica tablas propias no definidas en SDD.
- No modificar codigo de aplicacion en esta tarea.
- No anadir dependencias de Neo4j, frontend, scraping ni observabilidad.

Criterios de aceptacion:
- Los paquetes son importables con `uv`.
- `pyproject.toml` no contiene `neo4j`.
- El lockfile queda actualizado.

Errores probables a evitar:
- Anadir una libreria que cree una coleccion vectorial fuera de `document_chunks`.
- Mezclar cambios de dependencias con implementacion de RAG.

Edge cases obligatorios:
- Si `uv` resuelve dependencias transitivas, no duplicarlas manualmente salvo necesidad real.
- Si la instalacion requiere red y falla, reportar bloqueo tecnico; no editar lockfile a mano.

Stop conditions:
- La dependencia elegida obliga a cambiar el modelo de datos.
- La tarea requiere actualizar SDD de arquitectura.

Comandos de verificacion:
- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "from langchain_core.runnables import RunnableLambda; from langchain_openai import ChatOpenAI, OpenAIEmbeddings; import pgvector; print('rag deps ok')"`
- `cd hydra/backend && uv run python -c "import pathlib; text=pathlib.Path('pyproject.toml').read_text().lower(); assert 'neo4j' not in text; print('no neo4j dependency')"`

## TASK-RAG-002: Definir constantes RAG

Estado: review
Prioridad: must

Objetivo:
Centralizar constantes RAG sin crear nuevas variables de entorno.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_config.py`

Dependencias:
- TASK-RAG-001

Requisitos:
- Crear `EMBEDDING_DIMENSION = 4096`.
- Crear `DEFAULT_TOP_K = 5`.
- Crear `EVIDENCE_SNIPPET_CHARS` con un valor prudente para evitar devolver documentos completos.
- No leer Settings ni entorno en import time.
- No abrir DB ni crear clientes de modelo.

Criterios de aceptacion:
- Las constantes son importables.
- La dimension coincide con `sdd/02-data-model.md` y `db_schema.py`.

Errores probables a evitar:
- Definir una dimension distinta a `4096`.
- Crear variables de entorno nuevas para estos valores.

Edge cases obligatorios:
- El modulo debe importar aunque falten `.env` y `MODEL_API_KEY`.
- `EVIDENCE_SNIPPET_CHARS` debe ser mayor que cero.

Stop conditions:
- Se necesita cambiar la dimension o el default `top_k` del SDD.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_config import EMBEDDING_DIMENSION, DEFAULT_TOP_K, EVIDENCE_SNIPPET_CHARS; assert EMBEDDING_DIMENSION==4096 and DEFAULT_TOP_K==5 and EVIDENCE_SNIPPET_CHARS>0; print('rag constants ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db_schema import SCHEMA_STATEMENTS; sql='\n'.join(SCHEMA_STATEMENTS); assert 'vector(4096)' in sql; print('schema dimension ok')"`

## TASK-RAG-003: Validar QueryRequest

Estado: review
Prioridad: must

Objetivo:
Asegurar que `POST /query` recibe preguntas no vacias y `top_k` valido antes de ejecutar retrieval.

Archivos permitidos:
- `hydra/backend/src/hydra_api/schemas.py`

Dependencias:
- TASK-RAG-002

Requisitos:
- Mantener campos del contrato: `question` y `top_k`.
- `question` debe rechazarse si esta vacia o solo contiene espacios.
- `top_k` debe tener default `5`.
- `top_k` debe rechazar valores menores que `1`.
- No anadir campos nuevos al request.
- No tocar schemas de briefing, evals, extracciones ni grafo.

Criterios de aceptacion:
- `QueryRequest(question='texto')` usa `top_k=5`.
- `QueryRequest(question='   ')` falla.
- `QueryRequest(question='texto', top_k=0)` falla.

Errores probables a evitar:
- Cambiar el nombre de `question` o `top_k`.
- Permitir `top_k=0` y luego devolver contexto vacio ambiguo.

Edge cases obligatorios:
- Preguntas con espacios alrededor deben normalizarse o al menos validarse como no vacias.
- Mensajes de error no deben incluir secretos ni stack traces.

Stop conditions:
- Se necesita cambiar el contrato de API documentado.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from pydantic import ValidationError; from hydra_api.schemas import QueryRequest; assert QueryRequest(question='Que pasa?').top_k==5; [QueryRequest(question='x', top_k=1)]; print('valid query ok')"`
- `cd hydra/backend && uv run python -c 'from pydantic import ValidationError; from hydra_api.schemas import QueryRequest; ns={"QueryRequest":QueryRequest,"ValidationError":ValidationError}; exec("bad=0\ntry:\n    QueryRequest(question=\"   \")\nexcept ValidationError:\n    bad+=1\ntry:\n    QueryRequest(question=\"x\", top_k=0)\nexcept ValidationError:\n    bad+=1\nassert bad==2\nprint(\"invalid query rejected\")", ns)'`

## TASK-RAG-004: Crear factory lazy de embeddings

Estado: review
Prioridad: must

Objetivo:
Crear un wrapper de embeddings compatible con OpenAI usando Settings existentes y sin llamadas en import time.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_embeddings.py`

Dependencias:
- TASK-RAG-001
- TASK-RAG-002

Requisitos:
- Crear `create_embedding_model(settings: Settings | None = None)`.
- Usar `HYDRA_EMBEDDING_MODEL` via `settings.hydra_embedding_model`.
- Usar `MODEL_API_KEY` y `MODEL_API_BASE_URL` via Settings existentes.
- No leer `.env` ni Settings al importar el modulo.
- No llamar al proveedor durante construccion ni import.
- No imprimir claves ni base URL completa con credenciales.

Criterios de aceptacion:
- El modulo importa sin variables de entorno.
- Con Settings fake, se puede construir el objeto sin red.

Errores probables a evitar:
- Usar `OPENAI_API_KEY` en vez de `MODEL_API_KEY`.
- Ejecutar una llamada de embedding en el constructor.

Edge cases obligatorios:
- Base URL custom compatible OpenAI debe conservarse.
- API key fake debe servir para verificaciones sin red.

Stop conditions:
- La libreria fuerza una llamada externa al instanciar el cliente.
- Se requiere renombrar variables de entorno.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.rag_embeddings as m; assert hasattr(m, 'create_embedding_model'); print('embedding module import ok')"`
- `cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.rag_embeddings import create_embedding_model; emb=create_embedding_model(); assert emb is not None; print('embedding factory ok')"`

## TASK-RAG-005: Validar vectores de embedding

Estado: review
Prioridad: must

Objetivo:
Evitar persistir o consultar embeddings con dimension incorrecta.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_embeddings.py`

Dependencias:
- TASK-RAG-004

Requisitos:
- Crear `validate_embedding_vector(vector, expected_dimension=EMBEDDING_DIMENSION) -> list[float]`.
- Aceptar solo secuencias numericas finitas.
- Rechazar longitud distinta a `4096`.
- Rechazar valores no numericos o `NaN`.
- No truncar ni rellenar vectores automaticamente.

Criterios de aceptacion:
- Un vector de `4096` floats pasa.
- Un vector de `3` floats falla.
- Un vector con `NaN` falla.

Errores probables a evitar:
- Corregir silenciosamente dimensiones malas.
- Persistir strings no numericos como vector.

Edge cases obligatorios:
- Tuplas y listas deben tratarse de forma consistente.
- El error no debe incluir el vector completo.

Stop conditions:
- El modelo configurado no devuelve 4096 dimensiones.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_embeddings import validate_embedding_vector; v=validate_embedding_vector([0.0]*4096); assert len(v)==4096; print('valid embedding ok')"`
- `cd hydra/backend && uv run python -c 'from hydra_api.rag_embeddings import validate_embedding_vector; import math; ns={"validate_embedding_vector":validate_embedding_vector,"math":math,"ValueError":ValueError}; exec("bad=0\nfor v in ([0.0]*3, [math.nan]*4096):\n    try:\n        validate_embedding_vector(v)\n    except ValueError:\n        bad+=1\nassert bad==2\nprint(\"bad embeddings rejected\")", ns)'`

## TASK-RAG-006: Crear modulo de storage RAG sin efectos en import

Estado: review
Prioridad: must

Objetivo:
Crear el modulo que contendra queries SQL RAG sin abrir conexiones ni depender de modelos al importar.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_store.py`

Dependencias:
- TASK-DB-011
- TASK-RAG-002

Requisitos:
- Crear tipos internos pequenos para chunks pendientes y resultados vectoriales.
- No importar `get_settings()` ni crear conexiones en import time.
- No llamar modelos.
- Documentar que el storage usa `documents` y `document_chunks`.
- No crear tablas ni modificar schema.

Criterios de aceptacion:
- `hydra_api.rag_store` importa sin DB ni `.env`.
- El codigo no contiene `CREATE TABLE`.

Errores probables a evitar:
- Abrir conexion al importar.
- Duplicar schemas canonicos de Pydantic innecesariamente.

Edge cases obligatorios:
- El modulo debe poder importarse con DB apagada.
- Los tipos no deben depender de pgvector en import si no es necesario.

Stop conditions:
- Hace falta cambiar `db_schema.py` para que el modulo importe.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.rag_store as s; print('rag store import ok')"`
- `cd hydra/backend && uv run python -c "import inspect, hydra_api.rag_store as s; src=inspect.getsource(s).upper(); assert 'CREATE TABLE' not in src; print('no schema creation in rag store')"`

## TASK-RAG-007: Seleccionar chunks pendientes de embedding

Estado: review
Prioridad: must

Objetivo:
Leer de forma acotada los chunks que todavia no tienen embedding.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_store.py`

Dependencias:
- TASK-RAG-006
- TASK-CORPUS-024

Requisitos:
- Crear `fetch_chunks_without_embeddings(cur, limit: int)`.
- Validar `limit >= 1`.
- Consultar solo `document_chunks` con `embedding IS NULL`.
- Ordenar por `document_id` y `chunk_index` para reproducibilidad.
- Devolver solo `id`, `document_id`, `chunk_index`, `content`, `metadata`.
- Usar SQL parametrizado.

Criterios de aceptacion:
- La funcion es importable.
- La query incluye `embedding IS NULL`.
- `limit=0` falla antes de ejecutar SQL.

Errores probables a evitar:
- Leer documentos completos fuera de chunks.
- Usar `LIMIT` interpolado con f-string.

Edge cases obligatorios:
- Tabla vacia debe devolver lista vacia.
- Metadata JSON nula o no dict debe normalizarse de forma segura o fallar claro.

Stop conditions:
- Se requiere acceder a rutas raw o documentos reales.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_store import fetch_chunks_without_embeddings; print(callable(fetch_chunks_without_embeddings))"`
- `cd hydra/backend && uv run python -c "import inspect; from hydra_api import rag_store; src=inspect.getsource(rag_store.fetch_chunks_without_embeddings); assert 'embedding IS NULL' in src and 'LIMIT' in src; print('pending chunk query ok')"`

## TASK-RAG-008: Actualizar embedding de chunk existente

Estado: review
Prioridad: must

Objetivo:
Persistir embeddings validados sin crear chunks nuevos ni modificar metadatos.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_store.py`

Dependencias:
- TASK-RAG-005
- TASK-RAG-007

Requisitos:
- Crear `update_chunk_embedding(cur, chunk_id: str, embedding) -> None`.
- Validar dimension con `validate_embedding_vector` antes del `UPDATE`.
- Actualizar solo `document_chunks.embedding` del `id` indicado.
- Usar SQL parametrizado.
- No cambiar `content`, `metadata`, `document_id`, `chunk_index` ni `documents.processing_status`.
- No hacer commit dentro del helper.

Criterios de aceptacion:
- La funcion es importable.
- La query contiene `UPDATE document_chunks`.
- El helper rechaza vector corto antes de ejecutar SQL.

Errores probables a evitar:
- Hacer upsert de chunks y resetear contenido/metadata por accidente.
- Commit/rollback dentro de helper de bajo nivel.

Edge cases obligatorios:
- `chunk_id` vacio debe fallar.
- Embedding con dimension incorrecta no debe ejecutar SQL.

Stop conditions:
- Psycopg/pgvector no puede serializar el vector sin cambiar schema.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_store import update_chunk_embedding; print(callable(update_chunk_embedding))"`
- `cd hydra/backend && uv run python -c "import inspect; from hydra_api import rag_store; src=inspect.getsource(rag_store.update_chunk_embedding); assert 'UPDATE document_chunks' in src and 'validate_embedding_vector' in src; print('embedding update helper ok')"`

## TASK-RAG-009: Crear servicio de indexacion inyectable

Estado: review
Prioridad: must

Objetivo:
Orquestar seleccion, calculo y persistencia de embeddings con dependencias inyectables para pruebas sin red.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_indexing.py`

Dependencias:
- TASK-RAG-004
- TASK-RAG-008

Requisitos:
- Crear `RagIndexingService` o funcion equivalente.
- Aceptar `connection_factory` y `embedding_model` inyectables.
- No crear cliente real ni conexion real si se pasan fakes.
- Procesar lotes acotados por `limit`.
- Commit solo despues de actualizar el lote completo.
- Rollback si falla una actualizacion.
- No imprimir textos completos de chunks ni embeddings.

Criterios de aceptacion:
- Puede probarse con fake cursor y fake embedding model.
- Rechaza `limit <= 0`.
- No hace llamadas externas si se inyecta fake model.

Errores probables a evitar:
- Llamar al proveedor real en unit smoke.
- Persistir lote parcial sin rollback claro.

Edge cases obligatorios:
- Lista de chunks pendiente vacia debe devolver contador `0`.
- Error en un vector debe abortar lote y no ocultarse como exito.

Stop conditions:
- Se necesita DB real o MODEL_API_KEY real para verificar la tarea.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.rag_indexing as m; assert hasattr(m, 'RagIndexingService'); print('rag indexing import ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_indexing import RagIndexingService; service=RagIndexingService(connection_factory=lambda: None, embedding_model=object()); print(service.__class__.__name__)"`

## TASK-RAG-010: Implementar busqueda vectorial sobre document_chunks

Estado: review
Prioridad: must

Objetivo:
Buscar chunks similares usando pgvector y la tabla canonica `document_chunks`.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_store.py`

Dependencias:
- TASK-RAG-005
- TASK-RAG-008
- TASK-DB-011

Requisitos:
- Crear `search_similar_chunks(cur, query_embedding, top_k: int)`.
- Validar embedding de query con dimension `4096`.
- Validar `top_k >= 1`.
- Excluir filas con `document_chunks.embedding IS NULL`.
- Hacer join con `documents` para obtener `title` y `source`.
- Usar distancia coseno de pgvector (`<=>`) o equivalente documentado.
- Convertir distancia a `score` comparable, preferiblemente `1 - cosine_distance`.
- Ordenar por menor distancia.
- Usar SQL parametrizado.

Criterios de aceptacion:
- La query referencia `document_chunks` y `documents`.
- La query excluye embeddings nulos.
- La funcion no requiere DB en import time.

Errores probables a evitar:
- Crear tabla LangChain paralela.
- Devolver chunks sin titulo/fuente.
- Tratar distancia como score alto sin convertir.

Edge cases obligatorios:
- Tabla sin embeddings debe devolver lista vacia.
- Score debe ser numerico aunque distancia venga como Decimal.
- `top_k=1` debe ser valido.

Stop conditions:
- No se puede parametrizar el vector sin interpolar contenido no confiable.
- Hace falta cambiar schema o crear tabla nueva.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_store import search_similar_chunks; print(callable(search_similar_chunks))"`
- `cd hydra/backend && uv run python -c "import inspect; from hydra_api import rag_store; src=inspect.getsource(rag_store.search_similar_chunks); assert 'document_chunks' in src and 'documents' in src and 'embedding IS NOT NULL' in src and '<=>' in src; print('vector search sql ok')"`

## TASK-RAG-011: Normalizar resultados recuperados

Estado: review
Prioridad: must

Objetivo:
Convertir resultados SQL en `RetrievedDocument` seguros para el contrato API.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_retriever.py`

Dependencias:
- TASK-RAG-002
- TASK-RAG-010

Requisitos:
- Crear helper para convertir filas/resultados internos a `RetrievedDocument`.
- Incluir `document_id`, `chunk_id`, `title`, `source`, `score`, `evidence`.
- Recortar `evidence` a `EVIDENCE_SNIPPET_CHARS`.
- No devolver documentos completos.
- No inventar titulo/fuente si faltan: usar fallback explicito o fallar seguro.

Criterios de aceptacion:
- Un resultado sintetico se convierte a `RetrievedDocument`.
- Evidence largo se recorta.
- Score se convierte a `float`.

Errores probables a evitar:
- Exponer `metadata` completa o texto completo.
- Omitir `chunk_id` y perder trazabilidad.

Edge cases obligatorios:
- Evidence vacio debe producir limitacion aguas arriba, no texto inventado.
- Score `None` debe fallar o normalizarse de forma segura.

Stop conditions:
- Se necesita cambiar `RetrievedDocument` del contrato API.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.rag_retriever as r; assert hasattr(r, 'to_retrieved_document'); print('retrieved normalizer import ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_retriever import to_retrieved_document; d=to_retrieved_document({'document_id':'doc','chunk_id':'c','title':'T','source':'S','score':0.5,'content':'x'*2000}); assert d.document_id=='doc' and len(d.evidence)<2000; print('retrieved document ok')"`

## TASK-RAG-012: Crear retriever LCEL inyectable

Estado: review
Prioridad: must

Objetivo:
Exponer retrieval como componente LangChain/LCEL sin acoplarlo a DB/modelos reales en pruebas.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_retriever.py`

Dependencias:
- TASK-RAG-004
- TASK-RAG-010
- TASK-RAG-011

Requisitos:
- Crear `create_retriever_runnable(...)` o equivalente LCEL.
- Aceptar `connection_factory` y `embedding_model` inyectables.
- Embeder solo la pregunta recibida, no documentos completos.
- Usar `top_k` validado.
- Devolver lista de `RetrievedDocument`.
- No abrir DB ni crear cliente real en import time.

Criterios de aceptacion:
- El retriever puede invocarse con fakes.
- El modulo importa sin DB ni `.env`.
- Si el fake devuelve lista vacia, el retriever devuelve `[]`.

Errores probables a evitar:
- Hacer retrieval en import time.
- Mezclar generacion de respuesta dentro del retriever.

Edge cases obligatorios:
- Pregunta vacia no debe llegar al retriever si `QueryRequest` funciona.
- Fallo de embedding debe propagarse como error seguro en capa servicio/endpoint.

Stop conditions:
- LCEL obliga a cambiar modelos o contrato.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_retriever import create_retriever_runnable; r=create_retriever_runnable(connection_factory=lambda: None, embedding_model=object()); assert r is not None; print('retriever runnable ok')"`

## TASK-RAG-013: Crear prompt de respuesta grounded

Estado: review
Prioridad: must

Objetivo:
Definir instrucciones de respuesta que obliguen a usar evidencias y limitaciones.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_answering.py`

Dependencias:
- TASK-RAG-011

Requisitos:
- Crear `build_answer_prompt(question, retrieved_documents)` o plantilla equivalente.
- Incluir reglas:
  - responder solo con contexto recuperado;
  - citar evidencias breves;
  - incluir limitaciones;
  - no afirmar coordinacion, intencion o atribucion sin evidencia explicita;
  - si falta contexto, decirlo claramente.
- No incluir documentos completos si solo se necesitan evidencias recortadas.
- No imprimir prompt en logs.

Criterios de aceptacion:
- El prompt incluye la pregunta y evidencias recortadas.
- El prompt incluye regla de no coordinacion sin evidencia.
- Con lista vacia, el helper produce instruccion de limitacion o delega al no-context path.

Errores probables a evitar:
- Pedir al modelo inferencias no respaldadas.
- Pasar contenido completo de documentos al prompt sin recorte.

Edge cases obligatorios:
- Evidence con saltos de linea debe mantenerse legible.
- Lista vacia no debe generar prompt que invite a inventar.

Stop conditions:
- Se necesita cambiar la politica analitica del producto.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_answering import build_answer_prompt; p=build_answer_prompt('q', []); assert 'limitacion' in p.lower() or 'contexto' in p.lower(); print('empty prompt safe')"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_answering import build_answer_prompt; p=build_answer_prompt('q', [{'evidence':'ev','document_id':'doc','chunk_id':'c','title':'T','source':'S','score':0.9}]); assert 'coordinacion' in p.lower() and 'ev' in p; print('grounded prompt ok')"`

## TASK-RAG-014: Crear chain de respuesta con modelo inyectable

Estado: review
Prioridad: must

Objetivo:
Generar respuestas analiticas usando LCEL y un chat model compatible, verificable con fake model.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_answering.py`

Dependencias:
- TASK-RAG-001
- TASK-RAG-013

Requisitos:
- Crear `create_chat_model(settings: Settings | None = None)` usando `HYDRA_CHAT_MODEL`, `MODEL_API_KEY` y `MODEL_API_BASE_URL` existentes.
- Crear `create_answer_chain(chat_model=None)` o equivalente.
- Permitir fake chat model en pruebas.
- No llamar proveedor real en import ni construccion.
- No registrar prompts completos ni respuestas completas.

Criterios de aceptacion:
- El modulo importa sin `.env`.
- Con fake model, el chain devuelve texto.
- Con Settings fake, se puede construir chat model sin red.

Errores probables a evitar:
- Usar otro modelo por defecto distinto de `qwen3.6` sin Settings.
- Llamar al modelo durante verificacion local.

Edge cases obligatorios:
- Error de modelo debe manejarse aguas arriba sin exponer secretos.
- Respuesta vacia del fake/modelo debe producir limitacion o error seguro.

Stop conditions:
- El proveedor exige credenciales reales durante construccion.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api.rag_answering as a; assert hasattr(a, 'create_answer_chain'); print('answering import ok')"`
- `cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.rag_answering import create_chat_model; model=create_chat_model(); assert model is not None; print('chat factory ok')"`

## TASK-RAG-015: Implementar respuesta sin contexto suficiente

Estado: review
Prioridad: must

Objetivo:
Bloquear respuestas inventadas cuando retrieval no devuelve evidencia util.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_answering.py`

Dependencias:
- TASK-RAG-011
- TASK-RAG-014

Requisitos:
- Crear `build_no_context_response(question, trace_id)` o equivalente.
- Devolver `QueryResponse` con:
  - `answer` indicando que no hay contexto suficiente;
  - `retrieved_documents=[]`;
  - `limitations` con al menos una limitacion explicita;
  - `trace_id` recibido.
- No llamar chat model si no hay documentos recuperados.
- No mencionar causas no verificadas.

Criterios de aceptacion:
- Con lista vacia, no se invoca modelo.
- La respuesta cumple schema `QueryResponse`.
- Incluye limitacion sobre corpus disponible.

Errores probables a evitar:
- Generar una respuesta generica no basada en corpus.
- Devolver HTTP error en vez de respuesta analitica con limitacion para ausencia de contexto.

Edge cases obligatorios:
- Pregunta valida pero DB sin embeddings debe entrar en este path.
- `trace_id` local debe preservarse.

Stop conditions:
- Producto decide que ausencia de contexto debe ser otro codigo HTTP.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_answering import build_no_context_response; r=build_no_context_response('q','trace-local'); assert r.retrieved_documents==[] and r.limitations and r.trace_id=='trace-local'; print('no context response ok')"`

## TASK-RAG-016: Crear servicio de consulta RAG

Estado: review
Prioridad: must

Objetivo:
Orquestar validation, retrieval, respuesta grounded y fallback sin contexto para `POST /query`.

Archivos permitidos:
- `hydra/backend/src/hydra_api/rag_service.py`

Dependencias:
- TASK-RAG-012
- TASK-RAG-014
- TASK-RAG-015

Requisitos:
- Crear `QueryService` o funcion equivalente.
- Aceptar retriever y answer_chain inyectables.
- Generar `trace_id` local seguro si no hay Langfuse.
- Si retrieval devuelve `[]`, usar no-context path sin llamar modelo.
- Si hay documentos, generar respuesta con prompt grounded.
- Construir `QueryResponse` segun contrato.
- No abrir DB/modelos en import time.
- No imprimir pregunta completa, evidencias completas, secretos ni stack traces.

Criterios de aceptacion:
- Servicio importable sin `.env` ni DB.
- Con retriever fake vacio devuelve no-context response.
- Con retriever fake con evidencia y answer fake devuelve respuesta con documentos.

Errores probables a evitar:
- Mezclar FastAPI route con logica RAG interna.
- Omitir `trace_id`.

Edge cases obligatorios:
- Retriever devuelve documentos pero answer fake/modelo devuelve texto vacio: debe producir limitacion o error seguro.
- Excepcion de retriever/modelo debe poder mapearse a error seguro en endpoint.

Stop conditions:
- Se requiere Langfuse real para generar `trace_id`.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; print(callable(QueryService))"`
- `cd hydra/backend && uv run python -c "from hydra_api.rag_service import QueryService; from hydra_api.schemas import QueryRequest; s=QueryService(retriever=lambda q,k: [], answer_chain=lambda *a, **k: 'x'); r=s.query(QueryRequest(question='q')); assert r.retrieved_documents==[] and r.limitations and r.trace_id; print('query service no-context ok')"`

## TASK-RAG-017: Exponer POST /query en FastAPI

Estado: review
Prioridad: must

Objetivo:
Conectar el servicio RAG al endpoint `POST /query` respetando el contrato API.

Archivos permitidos:
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/rag_service.py`
- `hydra/backend/src/hydra_api/errors.py`

Dependencias:
- TASK-RAG-003
- TASK-RAG-016

Requisitos:
- Crear ruta `POST /query`.
- Request: `QueryRequest`.
- Response: `QueryResponse`.
- Permitir inyectar servicio fake en tests, por ejemplo via `app.state.query_service`.
- Si no hay fake, construir servicio real de forma lazy al recibir request.
- Mapear errores esperados a respuestas seguras sin stack trace.
- No exponer secretos, headers ni detalles internos.
- No tocar otros endpoints salvo imports necesarios.

Criterios de aceptacion:
- `/health` sigue funcionando.
- `/query` puede probarse con fake service sin DB ni modelo real.
- OpenAPI incluye `POST /query`.

Errores probables a evitar:
- Crear el servicio real al importar `main.py`.
- Romper handlers de errores existentes.

Edge cases obligatorios:
- Body invalido debe devolver error seguro de FastAPI/Pydantic.
- Servicio fake que devuelve `QueryResponse` debe pasar tal cual.

Stop conditions:
- Implementar `/query` requiere DB/modelo real para arrancar la app.
- Hace falta cambiar el contrato documentado.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; assert TestClient(app).get('/health').json()['status']=='ok'; print('health ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; from hydra_api.schemas import QueryResponse; Fake=type('Fake', (), {'query': lambda self, request: QueryResponse(answer='Sin contexto suficiente.', retrieved_documents=[], limitations=['Corpus sin embeddings.'], trace_id='trace-test')}); app.state.query_service=Fake(); res=TestClient(app).post('/query', json={'question':'q','top_k':5}); assert res.status_code==200 and res.json()['trace_id']=='trace-test'; del app.state.query_service; print('query fake endpoint ok')"`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; schema=TestClient(app).get('/openapi.json').json(); assert '/query' in schema['paths']; print('openapi query ok')"`

## TASK-RAG-018: Ejecutar carga real de embeddings

Estado: blocked
Prioridad: must

Bloqueo:
Depende de corpus real aprobado, chunks persistidos en PostgreSQL, DB local inicializada y `MODEL_API_KEY` real configurada en `.env` local no versionado.

Objetivo:
Calcular y persistir embeddings reales para chunks del corpus cerrado.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-RAG-009
- TASK-CORPUS-031
- TASK-DB-020

Requisitos:
- Ejecutar el servicio de indexacion contra DB local.
- Usar `HYDRA_EMBEDDING_MODEL=qwen3-embedding`.
- Confirmar que todos los embeddings tienen `4096` dimensiones.
- No imprimir API keys, embeddings completos ni chunks completos.
- No borrar documentos ni chunks.

Criterios de aceptacion:
- Chunks del corpus aprobado quedan con `embedding IS NOT NULL`.
- No hay errores de dimension.
- El reporte indica conteos, no contenido completo.

Errores probables a evitar:
- Ejecutar sobre corpus no aprobado.
- Versionar `.env` o documentos reales sin aprobacion.

Edge cases obligatorios:
- Si el proveedor devuelve dimension distinta, abortar sin persistir lote parcial.
- Si la DB no esta inicializada, parar y reportar.

Stop conditions:
- Falta corpus, DB o clave real.
- Hay dudas sobre coste o proveedor de embeddings.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_indexing import RagIndexingService; print('indexing service ready')"`
- `cd hydra/backend && uv run python -c "from hydra_api.db import get_connection; conn=get_connection(); cur=conn.cursor(); cur.execute('SELECT count(*) FROM document_chunks WHERE embedding IS NOT NULL'); print(cur.fetchone()[0]); conn.close()"`

## TASK-RAG-019: Verificar retrieval real en pgvector

Estado: blocked
Prioridad: must

Bloqueo:
Depende de TASK-RAG-018 y de DB local con embeddings reales.

Objetivo:
Comprobar que una pregunta de prueba recupera chunks trazables con scores.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-RAG-010
- TASK-RAG-018

Requisitos:
- Ejecutar una busqueda real con pregunta del dominio aprobado.
- Confirmar que los resultados incluyen `document_id`, `chunk_id`, `title`, `source`, `score`, `evidence`.
- No imprimir documentos completos.
- No afirmar calidad analitica todavia; solo retrieval tecnico.

Criterios de aceptacion:
- Retrieval devuelve entre `1` y `top_k` resultados si hay corpus suficiente.
- Scores son numericos.
- Evidencias son fragmentos breves.

Errores probables a evitar:
- Tratar resultados vacios como exito si hay embeddings cargados.
- Copiar contenido completo de chunks al reporte.

Edge cases obligatorios:
- Pregunta fuera de dominio puede devolver pocos resultados y debe reportarse como limitacion.
- Chunks duplicados deben mantener `chunk_id` distinto.

Stop conditions:
- No hay embeddings reales.
- La query requiere cambiar schema o crear indices nuevos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.rag_store import search_similar_chunks; print('manual smoke requires real query embedding')"`

## TASK-RAG-020: Verificar POST /query con modelo real

Estado: blocked
Prioridad: must

Bloqueo:
Depende de TASK-RAG-018, TASK-RAG-019, `MODEL_API_KEY` real y decision explicita de ejecutar llamadas de modelo.

Objetivo:
Validar end-to-end que `/query` devuelve respuesta, documentos recuperados, limitaciones y `trace_id`.

Archivos permitidos:
- Ninguno

Dependencias:
- TASK-RAG-017
- TASK-RAG-019

Requisitos:
- Ejecutar contra backend local.
- Usar pregunta de demo acordada.
- Verificar que la respuesta incluye evidencias y limitaciones.
- Verificar que no afirma coordinacion/atribucion sin evidencia explicita.
- No publicar prompt, headers, API keys ni respuesta completa si contiene texto largo.

Criterios de aceptacion:
- HTTP 200 con shape de `QueryResponse`.
- `retrieved_documents` incluye trazabilidad.
- `trace_id` existe.
- Si no hay contexto, devuelve limitacion y no inventa.

Errores probables a evitar:
- Ejecutar llamadas reales sin aprobacion.
- Copiar secretos o headers en el reporte.

Edge cases obligatorios:
- Pregunta sin contexto debe activar no-context path.
- Error de proveedor debe devolver error seguro.

Stop conditions:
- Falta clave real, DB viva o aprobacion de coste.
- La respuesta incumple reglas de evidencia.

Comandos de verificacion:
- `cd hydra/backend && uv run uvicorn hydra_api.main:app --reload`
- `curl -sS http://localhost:8000/query -H 'content-type: application/json' -d '{"question":"Pregunta de demo acordada","top_k":5}'`
