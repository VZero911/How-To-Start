# How-To-Start

Entry point for **how to start V0 projects and deploys**.

This repository is documentation and planning only — a set of clear HOW-TO / DESIGN notes
to read **before** writing any implementation. Nothing here runs, and nothing here spends
money. Each guide is meant to be lifted into its own implementation repository later, once
the design is signed off.

## Conventions (apply to every guide)

- **Language:** English everywhere.
- **Currency:** USD (`$`) is the default unit; on-chain amounts are USDC.
- **Numbers:** format large numbers (`1000` → `1K`, `1000000` → `1M`).
- **Secrets:** no real keys or credentials in any repository. Ship a `.env.example` with
  placeholder values and keep the real `.env` out of version control.
- **Networking:** services bind to localhost and keep a small liveness/status check.
- **Commits:** Conventional Commits.

## Index

| Guide | What it covers |
| --- | --- |
| [`docs/fleet-deploy.md`](docs/fleet-deploy.md) | Concept-level design for a Dockerized, cost-optimized model API task runner ("fleet node") that does the maximum useful work inside a **hard $100 USD** token budget, then stops. Budget-governor concept, pricing/model assumptions, cost optimizations, and the $100-cap guarantee. |

## How to use this repo

1. Pick the deploy you want to start from the index above.
2. Read the guide top-to-bottom; it states its **assumptions** explicitly so they can be
   corrected before any code is written.
3. When the design is approved, scaffold a **new** implementation repository from the guide —
   do not build inside `How-To-Start`.
4. Keep this repo as the living plan: update a guide as decisions change.

## Status

- `docs/fleet-deploy.md` — **DESIGN / PLAN** (not yet implemented).
