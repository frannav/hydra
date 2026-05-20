# Follow-up Repair - Mission 06 Council y briefing

## Objetivo

Corregir el bloqueante restante del repair de Mission 06: el council creado por `create_council_service()` no puede ejecutarse con modelos LangChain reales porque `ChatOpenAI` no es callable directo y `CouncilService.run()` invoca las chains con `chain(prompt)`.

## Veredicto de revision

El repair de Mission 06 no queda aprobado hasta aplicar este follow-up.

Los checks del repair pasan con lambdas/fakes callables, pero no cubren la forma real de las chains creadas por la factory.

## Bloqueante

`create_council_service()` construye `ChatOpenAI` directamente en `backend/src/hydra_api/council_service.py`, lineas 353-368, y los pasa a `CouncilService`.

`CouncilService.run()` los ejecuta con:

- `self.analyst_chain(analyst_prompt)`
- `self.evidence_reviewer_chain(evidence_prompt)`
- `self.risk_reviewer_chain(risk_prompt)`
- `self.final_synthesizer_chain(synthesizer_prompt)`

Pero `ChatOpenAI` no es callable directo; expone `.invoke(...)`.

Verificacion que reproduce el fallo sin llamar red:

```bash
cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.council_service import create_council_service; s=create_council_service(); assert hasattr(s.analyst_chain, 'invoke') and not callable(s.analyst_chain); print('real council chain is invoke-only')"
```

## Archivos permitidos

- `hydra/backend/src/hydra_api/council_service.py`
- `hydra/backend/src/hydra_api/model_client.py` solo si se decide reutilizar `build_chain()` para envolver modelos.

## Archivos prohibidos

- `hydra/frontend/**`
- `.env`, `.env.local` o cualquier archivo con secretos reales
- `hydra/backend/data/**`
- DB schema, RAG store/retriever/indexing
- Neo4j, evals, observabilidad
- SDD contracts o schemas canonicos

## Requisitos

- Crear un helper interno seguro, por ejemplo `_invoke_chain(chain, prompt)`.
- El helper debe soportar:
  - callables fakes actuales: `chain(prompt)`;
  - LCEL/Runnable/modelos LangChain: `chain.invoke(prompt)`;
  - respuestas con `.content`, devolviendo su texto;
  - respuestas no textuales, convirtiendo de forma segura con `str(...)`.
- Usar el helper en los 4 pasos del council.
- Mantener compatibilidad con fakes callables usados por los checks existentes.
- No llamar proveedor real en verificaciones.
- No imprimir prompts completos ni respuestas completas.
- No usar red, DB, corpus real ni Langfuse.

## Criterios de aceptacion

- `CouncilService` funciona con fakes callables.
- `CouncilService` funciona con objetos no callables que implementan `.invoke(prompt)`.
- `create_council_service()` con env fake sigue construyendo servicio sin red.
- Las chains reales creadas por factory son invocables por `CouncilService.run()` en terminos de interfaz; el smoke real con proveedor sigue bloqueado por SDD.

## Comandos de verificacion

```bash
cd hydra/backend && uv run python -c "from hydra_api.council_service import CouncilService; from hydra_api.schemas import RetrievedDocument; s=CouncilService(analyst_chain=lambda p:'draft', evidence_reviewer_chain=lambda p:'{\"evidence_supported\": true, \"unsupported_claims\": [], \"risk_review\": \"ok\"}', risk_reviewer_chain=lambda p:'{\"risk_level\": \"alto\", \"risk_review\": \"alto por evidencia\"}', final_synthesizer_chain=lambda p:'# Briefing\\n\\n## Limitaciones\\n- corpus'); r=s.run('q', [RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')]); assert r.council_review.evidence_supported is True and r.risk_level.value=='alto'; print('callable chains still ok')"
cd hydra/backend && uv run python -c "from hydra_api.council_service import CouncilService; from hydra_api.schemas import RetrievedDocument; InvokeOnly=type('InvokeOnly', (), {'__init__': lambda self, content: setattr(self, 'content', content), 'invoke': lambda self, prompt: type('Msg', (), {'content': self.content})()}); s=CouncilService(analyst_chain=InvokeOnly('draft'), evidence_reviewer_chain=InvokeOnly('{\"evidence_supported\": true, \"unsupported_claims\": [], \"risk_review\": \"ok\"}'), risk_reviewer_chain=InvokeOnly('{\"risk_level\": \"alto\", \"risk_review\": \"alto por evidencia\"}'), final_synthesizer_chain=InvokeOnly('# Briefing\\n\\n## Limitaciones\\n- corpus')); r=s.run('q', [RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')]); assert r.council_review.evidence_supported is True and r.risk_level.value=='alto' and r.briefing_markdown.startswith('# Briefing'); print('invoke-only chains ok')"
cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.council_service import create_council_service; s=create_council_service(); assert hasattr(s.analyst_chain, 'invoke') or callable(s.analyst_chain); print('real council factory interface ok')"
```

## Checks finales

Despues de aplicar este follow-up, reejecutar tambien los checks de:

- `sdd/tasks/06-council-briefing/06-council-briefing-repair.md`
- checks originales no bloqueados de Mission 06

No ejecutar `TASK-COUNCIL-008` ni `TASK-BRIEF-007`; siguen bloqueadas hasta tener corpus, DB, claves reales y aprobacion explicita de coste/red.
