# Second Follow-up Repair - Mission 06 Council y briefing

## Objetivo

Corregir la regresion introducida por el primer follow-up: `_invoke_chain()` soporta objetos `.invoke()`, pero convierte respuestas `dict` de fakes callables a `str(dict)`, rompiendo los checks originales de `CouncilService` con reviewers fake que devuelven diccionarios.

## Veredicto de revision

El repair del repair no queda aprobado hasta aplicar este segundo follow-up.

## Bloqueante

El check original no bloqueado de Mission 06 vuelve a fallar:

```bash
cd hydra/backend && uv run python -c "from hydra_api.council_service import CouncilService; f=lambda prompt: 'ok'; s=CouncilService(analyst_chain=f, evidence_reviewer_chain=lambda p: {'evidence_supported': True, 'unsupported_claims': [], 'risk_review': 'ok'}, risk_reviewer_chain=lambda p: {'risk_level':'medio','risk_review':'ok'}, final_synthesizer_chain=lambda p: '# Briefing\n\n## Limitaciones\n- corpus'); r=s.run('q', []); assert r.briefing_markdown and r.council_review.evidence_supported is True and r.risk_level.value=='medio'; print('council service fake ok')"
```

Causa:

- `CouncilService._invoke_chain()` devuelve `str(response)` para respuestas sin `.content`.
- Cuando un reviewer fake devuelve `dict`, esto lo convierte a string Python con comillas simples.
- `_safe_parse_chain_output()` intenta `json.loads(...)`, falla, y devuelve `{}`.
- Resultado: `CouncilReview.evidence_supported=False`, rompiendo la compatibilidad con fakes `dict`.

## Archivos permitidos

- `hydra/backend/src/hydra_api/council_service.py`

## Archivos prohibidos

- `hydra/frontend/**`
- `.env`, `.env.local` o secretos reales
- `hydra/backend/data/**`
- DB schema, RAG store/retriever/indexing
- Neo4j, evals, observabilidad
- SDD contracts o schemas canonicos

## Requisitos

- `_invoke_chain()` debe preservar respuestas estructuradas (`dict`, `list`) sin convertirlas a string.
- Para respuestas con `.content`, debe devolver `str(response.content)`.
- Para respuestas textuales, debe devolver `str`.
- Para respuestas no textuales no estructuradas, puede devolver el objeto raw o convertirlo de forma segura segun el caller.
- `CouncilService.run()` debe:
  - convertir a texto solo las salidas de analyst y final synthesizer;
  - pasar salidas raw de evidence/risk reviewers a `_safe_parse_chain_output()`;
  - mantener compatibilidad con callables fakes, dict fakes, strings JSON e invoke-only fakes.
- No usar `eval`.
- No llamar proveedor real, DB, red, corpus ni Langfuse en verificaciones.

## Criterios de aceptacion

- El check original con reviewer fakes `dict` vuelve a pasar.
- El check de reviewer strings JSON sigue pasando.
- El check de invoke-only fake sigue pasando.
- `create_council_service()` con env fake sigue construyendo servicio sin red.

## Comandos de verificacion

```bash
cd hydra/backend && uv run python -c "from hydra_api.council_service import CouncilService; f=lambda prompt: 'ok'; s=CouncilService(analyst_chain=f, evidence_reviewer_chain=lambda p: {'evidence_supported': True, 'unsupported_claims': [], 'risk_review': 'ok'}, risk_reviewer_chain=lambda p: {'risk_level':'medio','risk_review':'ok'}, final_synthesizer_chain=lambda p: '# Briefing\\n\\n## Limitaciones\\n- corpus'); r=s.run('q', []); assert r.briefing_markdown and r.council_review.evidence_supported is True and r.risk_level.value=='medio'; print('dict fake reviewers ok')"
cd hydra/backend && uv run python -c "from hydra_api.council_service import CouncilService; from hydra_api.schemas import RetrievedDocument; s=CouncilService(analyst_chain=lambda p:'draft', evidence_reviewer_chain=lambda p:'{\"evidence_supported\": true, \"unsupported_claims\": [], \"risk_review\": \"ok\"}', risk_reviewer_chain=lambda p:'{\"risk_level\": \"alto\", \"risk_review\": \"alto por evidencia\"}', final_synthesizer_chain=lambda p:'# Briefing\\n\\n## Limitaciones\\n- corpus'); r=s.run('q', [RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')]); assert r.council_review.evidence_supported is True and r.risk_level.value=='alto'; print('string reviewers still ok')"
cd hydra/backend && uv run python -c "from hydra_api.council_service import CouncilService; from hydra_api.schemas import RetrievedDocument; InvokeOnly=type('InvokeOnly', (), {'__init__': lambda self, content: setattr(self, 'content', content), 'invoke': lambda self, prompt: type('Msg', (), {'content': self.content})()}); s=CouncilService(analyst_chain=InvokeOnly('draft'), evidence_reviewer_chain=InvokeOnly('{\"evidence_supported\": true, \"unsupported_claims\": [], \"risk_review\": \"ok\"}'), risk_reviewer_chain=InvokeOnly('{\"risk_level\": \"alto\", \"risk_review\": \"alto por evidencia\"}'), final_synthesizer_chain=InvokeOnly('# Briefing\\n\\n## Limitaciones\\n- corpus')); r=s.run('q', [RetrievedDocument(document_id='doc1', chunk_id='c1', title='T', source='S', score=0.8, evidence='ev')]); assert r.council_review.evidence_supported is True and r.risk_level.value=='alto' and r.briefing_markdown.startswith('# Briefing'); print('invoke-only reviewers still ok')"
cd hydra/backend && MODEL_API_KEY=fake MODEL_API_BASE_URL=https://example.invalid/v1 uv run python -c "from hydra_api.council_service import create_council_service; s=create_council_service(); assert hasattr(s.analyst_chain, 'invoke') or callable(s.analyst_chain); print('real council factory interface ok')"
```

## Checks finales

Despues de aplicar este segundo follow-up:

- Reejecutar los checks de este archivo.
- Reejecutar los checks de `06-council-briefing-repair-followup.md`.
- Reejecutar los checks de `06-council-briefing-repair.md`.
- Reejecutar los checks originales no bloqueados de Mission 06.

No ejecutar `TASK-COUNCIL-008` ni `TASK-BRIEF-007`; siguen bloqueados hasta tener corpus, DB, claves reales y aprobacion explicita de coste/red.

