# Tasks - Backend

## Reglas de atomizacion

- Ejecutar estas tareas en orden.
- No tocar frontend.
- No crear ni modificar `.env` reales.
- No crear documentacion nueva salvo que la tarea la liste en `Archivos permitidos` o el usuario lo pida explicitamente.
- No editar estados de tareas durante la ejecucion; el reviewer los cambia tras revisar.
- No hacer llamadas reales a proveedores de modelos en verificaciones.
- No ejecutar builds que generen artefactos locales salvo que la tarea lo pida.
- Si aparecen artefactos generados (`.venv/`, `dist/`, `build/`, `*.egg-info/`, `__pycache__/`), deben estar ignorados y no versionarse.
- Cada tarea debe reportar archivos modificados, comandos ejecutados, resultado y bloqueos.

## Lecciones incorporadas desde la primera mission backend

- Las verificaciones deben cubrir edge cases, no solo el happy path.
- El logging seguro debe probar claves sensibles en args estructurados y handlers preexistentes.
- `setup_logging()` debe ser idempotente y no dejar handlers inseguros.
- Los cambios documentales fuera de scope deben ser tarea separada o peticion explicita del usuario.
- La configuracion debe poder importarse sin secretos reales.
- El cliente de modelos no debe hacer llamadas de red en import time ni en pruebas.

## TASK-BACK-001: Inicializar backend con uv

Estado: done
Prioridad: must

Objetivo:
Crear un proyecto Python backend instalable con `uv`.

Archivos permitidos:
- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`

Requisitos:
- Usar layout `src`.
- Usar build backend PEP 517 valido:
  - `requires = ["hatchling"]`
  - `build-backend = "hatchling.build"`
- Incluir dependencias base:
  - `fastapi`
  - `uvicorn[standard]`
  - `pydantic`
  - `pydantic-settings`
- No incluir `setuptools` salvo que haya justificacion explicita.
- No versionar `.venv/`, `dist/`, `build/`, `*.egg-info/` ni `__pycache__/`.

Criterios de aceptacion:
- `uv sync` funciona.
- `pyproject.toml` tiene build-system estandar.
- No hay artefactos generados versionados.

Comandos de verificacion:
- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "import importlib.metadata; print(importlib.metadata.version('hydra-api'))"`
- `git status --ignored --short hydra/backend`

## TASK-BACK-002: Crear paquete hydra_api

Estado: done
Prioridad: must

Objetivo:
Crear el paquete Python base del backend.

Archivos permitidos:
- `hydra/backend/src/hydra_api/__init__.py`

Dependencias:
- TASK-BACK-001

Requisitos:
- Crear paquete importable `hydra_api`.
- No importar configuracion, FastAPI ni clientes externos desde `__init__.py`.
- No ejecutar codigo con efectos secundarios en import time.

Criterios de aceptacion:
- El paquete es importable.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import hydra_api; print(hydra_api.__name__)"`

## TASK-BACK-003: Crear configuracion

Estado: done
Prioridad: must

Objetivo:
Centralizar configuracion del backend con Pydantic Settings.

Archivos permitidos:
- `hydra/backend/src/hydra_api/config.py`
- `hydra/backend/.env.example`

Dependencias:
- TASK-BACK-001
- TASK-BACK-002

Requisitos:
- Usar `pydantic-settings`.
- Crear clase `Settings`.
- Leer estas variables:
  - `MODEL_API_KEY`
  - `MODEL_API_BASE_URL`
  - `HYDRA_CHAT_MODEL`
  - `HYDRA_REVIEW_MODEL`
  - `HYDRA_EMBEDDING_MODEL`
  - `LANGFUSE_PUBLIC_KEY`
  - `LANGFUSE_SECRET_KEY`
  - `LANGFUSE_BASE_URL`
  - `DATABASE_URL`
- Usar `.env` local como fuente opcional.
- No leer `.env.example` como configuracion real.
- No instanciar settings en import time si eso exige secretos reales.
- Crear `get_settings()` cacheada.
- Mantener valores ficticios en `backend/.env.example`.
- No hardcodear secretos.

Criterios de aceptacion:
- `hydra_api.config` importa sin secretos reales.
- `Settings` puede instanciarse con valores ficticios.
- `get_settings()` existe y es callable.
- Pydantic muestra error claro si falta una variable obligatoria.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.config import Settings; s = Settings(model_api_key='replace_me', model_api_base_url='https://model-provider.example/v1', langfuse_public_key='replace_me', langfuse_secret_key='replace_me', database_url='postgresql+psycopg://hydra:hydra@localhost:5432/hydra'); print(s.hydra_chat_model)"`
- `cd hydra/backend && uv run python -c "from hydra_api.config import get_settings; print(callable(get_settings))"`
- `cd hydra/backend && MODEL_API_KEY=abc MODEL_API_BASE_URL=https://model-provider.example/v1 LANGFUSE_PUBLIC_KEY=pub LANGFUSE_SECRET_KEY=sec DATABASE_URL=postgresql+psycopg://hydra:hydra@localhost:5432/hydra uv run python -c "from hydra_api.config import Settings; print(Settings().model_api_key)"`

## TASK-BACK-004: Crear main FastAPI

Estado: done
Prioridad: must

Objetivo:
Crear la aplicacion FastAPI principal.

Archivos permitidos:
- `hydra/backend/src/hydra_api/main.py`

Dependencias:
- TASK-BACK-002
- TASK-BACK-003

Requisitos:
- Crear `app = FastAPI(...)`.
- No crear endpoints adicionales salvo `/health` si se ejecuta junto a TASK-BACK-005.
- No abrir conexiones DB ni clientes de modelos en import time.
- No imprimir secretos en startup.

Criterios de aceptacion:
- La app FastAPI importa y arranca.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.main import app; print(app.title)"`

## TASK-BACK-005: Crear healthcheck

Estado: done
Prioridad: must

Endpoint:
- `GET /health`

Archivos permitidos:
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/schemas.py` si ya existe

Dependencias:
- TASK-BACK-004

Requisitos:
- Devolver exactamente `{"status":"ok","service":"hydra-api"}`.
- No consultar DB ni proveedores externos.
- No exponer configuracion ni secretos.

Criterios de aceptacion:
- El endpoint responde `200`.
- La respuesta coincide con el contrato.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; r = TestClient(app).get('/health'); print(r.status_code, r.json()); assert r.status_code == 200; assert r.json() == {'status': 'ok', 'service': 'hydra-api'}"`

## TASK-BACK-006: Configurar CORS

Estado: done
Prioridad: must

Archivos permitidos:
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/config.py` si se necesita configuracion
- `hydra/backend/.env.example` si se documenta una variable publica de backend

Dependencias:
- TASK-BACK-003
- TASK-BACK-004

Requisitos:
- Permitir frontend local:
  - `http://localhost:3000`
  - `http://127.0.0.1:3000`
- No usar `allow_origins=["*"]` con `allow_credentials=True`.
- No abrir CORS innecesariamente en produccion.
- No incluir claves privadas ni `DATABASE_URL` en frontend.

Criterios de aceptacion:
- La app contiene middleware CORS.
- Los origenes permitidos son explicitos.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.main import app; print([m.cls.__name__ for m in app.user_middleware]); assert any(m.cls.__name__ == 'CORSMiddleware' for m in app.user_middleware)"`

## TASK-BACK-007: Manejo comun de errores

Estado: done
Prioridad: must

Archivos permitidos:
- `hydra/backend/src/hydra_api/errors.py`
- `hydra/backend/src/hydra_api/main.py`
- `hydra/backend/src/hydra_api/schemas.py` si ya existe

Dependencias:
- TASK-BACK-004

Requisitos:
- Crear formato comun:
  - `{ "error": { "code", "message", "details" } }`
- Manejar errores de dominio propios.
- Manejar `HTTPException`.
- Manejar excepciones inesperadas con mensaje generico.
- No exponer stack traces.
- No exponer headers completos.
- No exponer secretos ni URLs completas con credenciales.

Criterios de aceptacion:
- Los errores usan el formato comun.
- Las excepciones inesperadas devuelven mensaje seguro.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api.errors import error_response; print(error_response('x', 'safe'))"`
- `cd hydra/backend && uv run python -c "from hydra_api.main import app; print([getattr(k, '__name__', str(k)) for k in app.exception_handlers.keys()])"`

## TASK-BACK-008: Logging seguro

Estado: done
Prioridad: must

Archivos permitidos:
- `hydra/backend/src/hydra_api/logging.py`
- `hydra/backend/src/hydra_api/main.py` solo para llamar `setup_logging()`

Dependencias:
- TASK-BACK-004

Requisitos:
- No imprimir API keys.
- No imprimir secrets, tokens, passwords ni valores de `Authorization`.
- No imprimir headers completos.
- Enmascarar valores basandose en claves sensibles:
  - `api_key`
  - `secret`
  - `token`
  - `password`
  - `authorization`
  - `key`
- Soportar logging con args estructurados tipo dict.
- `setup_logging()` debe ser idempotente.
- Si ya existen `logging.StreamHandler`, todos deben quedar usando formatter seguro.
- No mutar `root.handlers` mientras se itera directamente.
- No anadir handlers duplicados si se llama varias veces.
- No afirmar que todo string arbitrario queda enmascarado; la garantia aplica a logging estructurado por claves sensibles.

Criterios de aceptacion:
- Un dict con clave `api_key` no imprime el valor completo.
- Varios handlers preexistentes no dejan filtraciones.
- Llamar `setup_logging()` dos veces no duplica handlers.
- `/health` sigue funcionando.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "import io, logging; from hydra_api.logging import _SensitiveFormatter; s=io.StringIO(); h=logging.StreamHandler(s); h.setFormatter(_SensitiveFormatter('%(message)s')); l=logging.getLogger('mask-test'); l.handlers.clear(); l.addHandler(h); l.setLevel(logging.INFO); l.propagate=False; l.info('payload %(api_key)s', {'api_key':'abcd12345678wxyz'}); out=s.getvalue(); print(out.strip()); assert 'abcd12345678wxyz' not in out"`
- `cd hydra/backend && uv run python - <<'PY'
import io
import logging
from hydra_api.logging import setup_logging, _SensitiveFormatter

root = logging.getLogger()
old_handlers = root.handlers[:]

try:
    s1 = io.StringIO()
    s2 = io.StringIO()
    h1 = logging.StreamHandler(s1)
    h2 = logging.StreamHandler(s2)
    h1.setFormatter(logging.Formatter("h1 %(message)s"))
    h2.setFormatter(logging.Formatter("h2 %(message)s"))
    root.handlers.clear()
    root.addHandler(h1)
    root.addHandler(h2)
    root.setLevel(logging.INFO)

    setup_logging()

    assert all(
        isinstance(h.formatter, _SensitiveFormatter)
        for h in root.handlers
        if isinstance(h, logging.StreamHandler)
    )
    logging.info("payload %(api_key)s", {"api_key": "abcd12345678wxyz"})
    combined = s1.getvalue() + s2.getvalue()
    print(combined.strip())
    assert "abcd12345678wxyz" not in combined

    count = len(root.handlers)
    setup_logging()
    assert len(root.handlers) == count
finally:
    root.handlers[:] = old_handlers
PY`
- `cd hydra/backend && uv run python -c "from fastapi.testclient import TestClient; from hydra_api.main import app; r = TestClient(app).get('/health'); print(r.status_code, r.json())"`

## TASK-BACK-009: Cliente de modelos

Estado: done
Prioridad: must

Archivos permitidos:
- `hydra/backend/src/hydra_api/model_client.py`
- `hydra/backend/pyproject.toml`
- `hydra/backend/uv.lock`

Dependencias:
- TASK-BACK-003

Requisitos:
- API compatible con OpenAI.
- Leer `MODEL_API_KEY` y `MODEL_API_BASE_URL` desde configuracion.
- No hardcodear proveedor ni URL real.
- No hacer llamadas de red en import time.
- No hacer llamadas reales en verificaciones.
- Si se anade dependencia (`openai` u otra), debe quedar en `pyproject.toml` y `uv.lock`.
- No registrar API keys ni headers.

Criterios de aceptacion:
- El factory del cliente es importable/callable.
- Crear el cliente no llama a la red.

Comandos de verificacion:
- `cd hydra/backend && uv sync`
- `cd hydra/backend && uv run python -c "from hydra_api.model_client import create_model_client; print(callable(create_model_client))"`

## TASK-BACK-010: Schemas Pydantic base

Estado: done
Prioridad: must

Archivos permitidos:
- `hydra/backend/src/hydra_api/schemas.py`

Dependencias:
- TASK-BACK-002

Requisitos:
- Schemas para documentos, metadatos, fuentes de ingesta, narrativas, chunks, query, briefing, errores, extracciones, proyeccion de grafo y evals.
- Separar schemas canonicos del dominio de schemas especificos de API.
- No acoplar schemas de extraccion a pgvector, Neo4j ni frontend.
- Seguir `sdd/02-data-model.md`.
- Seguir `sdd/03-api-contract.md`.
- Usar defaults seguros solo cuando el contrato lo permita.

Criterios de aceptacion:
- El modulo importa.
- `QueryRequest` aplica `top_k=5` por defecto.
- `HealthResponse` serializa el contrato de `/health`.
- Los schemas de extraccion/grafo no importan DB, pgvector, Neo4j ni frontend.

Comandos de verificacion:
- `cd hydra/backend && uv run python -c "from hydra_api import schemas; print('schemas ok')"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import QueryRequest; print(QueryRequest(question='test').top_k)"`
- `cd hydra/backend && uv run python -c "from hydra_api.schemas import HealthResponse; print(HealthResponse(status='ok', service='hydra-api').model_dump())"`
