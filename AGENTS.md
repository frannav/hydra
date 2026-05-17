# AGENTS.md — HYDRA

Minimal instructions for agents working in this repository.

## Project

HYDRA is a proof of concept for turning a closed corpus of public sources into traceable narrative intelligence.

## Source of truth

HYDRA follows SDD. This file only provides repository-level guidance.

Before changing code or documentation, read only the SDD files relevant to the task:

- `sdd/README.md`
- `sdd/01-architecture-decisions.md`
- `sdd/03-api-contract.md`
- `sdd/07-implementation-plan.md`
- `sdd/08-task-checklist.md`
- `sdd/tasks/<nn-domain>/<nn-domain>.md`

Use `docs/hydra-architecture.md` only when the SDD is not enough.
`docs/hydra-brainstorming.md` is historical; it is not a source of current decisions.

## Paths

The Git root is already `hydra/`.

- Do not create `hydra/hydra/`.
- If a task mentions `hydra/backend/...` and you are already at the repo root, edit `backend/...`.
- If a task mentions `hydra/frontend/...`, edit `frontend/...`.
- Keep backend, frontend, SDD, and docs separated as defined in the SDD.

## Tools

- Backend: `uv`.
- Frontend: `pnpm`.
- Do not mix package managers unless the SDD changes that decision.

## Workflow

- Work from atomic SDD tasks.
- Respect dependencies, priorities, and allowed files.
- Do not change architecture, stack, API contracts, models, or environment variable names without updating the SDD first or asking for confirmation.
- If something contradicts the SDD, stop and explain the contradiction.
- Keep changes small and reviewable.

## Security

- Do not hardcode secrets in code, Markdown, tests, or scripts.
- Use local `.env` files for real secrets.
- Commit only `.env.example` files with fake values.
- Do not expose keys, full headers, internal prompts, stack traces, or tokens in logs or API responses.
- The frontend must not contain private keys or call LLM providers directly.

## Critical product rules

- The frontend does not parse documents, chunk text, compute embeddings, or call models.
- All ingestion goes through the backend.
- Analytical responses must include evidence or limitations.
- Do not claim coordination, intent, or attribution without explicit evidence.
- Neo4j and frontend upload are optional extensions, not core MVP dependencies.

## Before closing a task

- Run the verification commands listed in the SDD.
- Review `git diff`.
- Confirm there are no secrets.
- Confirm no files outside the task scope were modified.
- Document any blocker or deviation.
