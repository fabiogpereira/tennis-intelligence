# ADR-003: Separate FastAPI and Next.js

## Context
The eventual product has Python-oriented data/modeling work and a TypeScript web experience.

## Options considered
A single full-stack framework, Python-rendered pages, or separate API and web applications.

## Decision
Keep FastAPI and Next.js as separate applications when implementation begins, joined by explicit versioned contracts.

## Why
The boundary matches the team’s likely language strengths and keeps research/modeling concerns separate from presentation.

## Trade-offs
There are two deployments and contract coordination. Do not build either application until Phase 1 establishes a validated user-facing need.

## Consequences
Integration tests and shared schemas become important once the boundary exists.
