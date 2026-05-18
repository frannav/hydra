# HYDRA Ontology

## Purpose

This directory contains the lightweight ontology for HYDRA.

The ontology is a **controlled vocabulary**, not a factual knowledge base.
It defines allowed IDs for narrative frames, actor types, affected sectors,
threat types, and graph node/edge types. It does not store facts about
documents, actors, or events.

## Files

- `hydra_ontology.yaml` — The ontology definition in YAML format.

## Validation

```bash
cd backend && uv run python -m hydra_api.ontology --validate ontology/hydra_ontology.yaml
```

This validates the YAML structure, checks for duplicate IDs, verifies
snake_case formatting, and confirms all required sections are present.

## No Models Executed

These commands only validate the ontology structure. They do not execute
any LLM models or make network requests.

> **no ejecuta modelos**: la validación de la ontología y los fixtures
> no ejecuta modelos ni llama a redes externas.
