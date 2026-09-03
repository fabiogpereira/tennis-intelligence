# Architecture

## Phase 1 boundary
There is no application or production pipeline yet. This repository establishes research contracts before implementation.

## Target shape

```text
source datasets -> source-specific ingestion -> normalized match/player records
                                                           |
                                                    feature generation
                                                           |
                                                    Tennis DNA research
                                                           |
                tested scoring/state and feature modules
                             /                    \
                       FastAPI                 Next.js
                   research API          editorial product UI
```

Research notebooks may call reusable modules but must not become the implementation boundary. PostgreSQL is deferred until a serving or collaboration requirement is demonstrated.

## Proposed repository structure

- `apps/web`: Next.js and TypeScript product experience.
- `apps/api`: FastAPI endpoints and API contracts.
- `research`: questions, literature, datasets, risks, experiments, notebooks.
- `pipelines`: ingestion, processing, feature generation.
- `models`: reusable scoring, Tennis DNA, and future pressure models.
- `packages/shared`: shared schemas and contracts where duplication becomes real.
- `skills`: review workflows for AI-assisted development.
- `docs`: methodology, architecture, AI transparency, and ADRs.
- `data`: schemas, manifests, and handling guidance; raw data remains external.
- `tests`: tennis domain, pipeline, model, and API tests.

## Explicit non-goals
Kubernetes, Kafka, microservices, premature PostgreSQL usage, framework-heavy abstractions, and player-facing Tennis DNA UI before feasibility validation are out of scope until a real constraint requires them.
