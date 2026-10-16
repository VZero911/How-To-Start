# How-To-Start

Entry point for **how to start V0 projects and deploys**.

This repository holds design notes and how-to guides. Read them **before** writing any
implementation. Nothing here runs, and nothing here spends money. Each guide is meant to be
lifted into its own implementation repository once the design is signed off.

## Prerequisites

To read the guides you need:

- `git`, to clone the repository.
- Any Markdown viewer (GitHub, an editor preview, or `less`).

To build what the guides describe (not required to read them):

- Docker and Docker Compose, for the containerised deploys.
- A model-provider API key. It belongs in your environment only,
  never in a file you commit.
- Python 3, if a guide's reference implementation is written in Python.

## Quick start

1. Clone this repository and open the index below.
2. Pick the guide that matches what you want to start.
3. Read it top to bottom. Each guide lists its **assumptions** explicitly, so you can
   correct them before any code is written.
4. When you start an implementation, copy `.env.example` into that new repository as `.env`,
   fill in your own values there, and keep `.env` out of version control. Do not create a
   `.env` in this repository.

## Conventions (apply to every guide)

- **Language:** English everywhere.
- **Currency:** USD (`$`) is the default unit. On-chain amounts are USDC.
- **Numbers:** format large numbers (`1000` becomes `1K`, `1000000` becomes `1M`).
- **Secrets:** no real keys or credentials in any repository. Ship a `.env.example` with
  placeholder values and keep the real `.env` out of version control.
- **Networking:** services bind to localhost and expose a small liveness and status check.
- **Commits:** Conventional Commits.

## Index

| Guide | What it covers |
| --- | --- |
| [`docs/fleet-deploy.md`](docs/fleet-deploy.md) | Concept-level design for a Dockerised, cost-optimised model API task runner (a "fleet node") that does the most useful work it can inside a **hard $100.00 USD** token budget, then stops. Covers the budget governor, pricing and model assumptions, cost optimisations, and the $100 cap guarantee. |

## Glossary

Terms used across the guides:

- **Fleet node:** one container that runs model API work as a set of concurrent workers.
- **Worker:** a task executor that calls the Messages API once per task.
- **Budget governor:** the component that reserves the worst-case cost of each call and
  refuses any call that would push spend past the cap.
- **Reservation:** the worst-case cost held before a call. It is replaced by the actual cost
  once the call finishes.
- **Ledger:** the persistent spend record. A restart reads it back so the budget resumes
  where it left off.
- **Prompt caching:** reuse of a stable prompt prefix, billed at a reduced read rate.
- **Batch API:** the asynchronous bulk path, billed at 50% of the standard rate.

## How to use this repo

1. Pick the deploy you want to start from in the index.
2. Read the guide top to bottom. Check its assumptions first.
3. When the design is approved, scaffold a **new** implementation repository from the guide.
   Do not build inside `How-To-Start`.
4. Keep this repository as the living plan. Update a guide as decisions change.

## Repository layout

```
How-To-Start/
├── .github/
│   └── workflows/
│       └── doc-lint.yml          # CI: relative links resolve, no key-shaped strings
├── docs/
│   └── fleet-deploy.md # design: $100-cap model API task runner
├── .env.example                  # placeholder configuration (no real values)
├── .gitignore
└── README.md
```

## Continuous integration

`doc-lint` runs on every push and pull request. It checks two things:

- Every relative Markdown link points to a file that exists.
- No real API keys appear anywhere in the repository.

## Status

- `docs/fleet-deploy.md`: **DESIGN / PLAN**, not yet implemented.
