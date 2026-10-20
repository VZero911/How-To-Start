# How-To-Start

Entry point for **how to start V0 projects and deploys**.

Guides, Docker quickstarts, and runnable examples for the public ALICE ecosystem.
Clone, read, build.

## Prerequisites

- `git`
- Docker and Docker Compose
- Python 3 (if a guide needs it)
- Any Markdown viewer (GitHub, editor, `less`)

## Quick start

```bash
git clone https://github.com/VZero911/How-To-Start.git
cd How-To-Start

# Run an alice-general worker node:
cd docker/alice-general
cp .env.example .env
docker compose up -d --build
curl http://localhost:8080/status
```

## Index

| Guide | What it covers |
| --- | --- |
| [`docs/alice-general-docker.md`](docs/alice-general-docker.md) | **Docker quickstart** for `alice-general` — minimum setup to run a task executor node. Dockerfile, docker-compose, env config, endpoints, scaling. Ready to `docker compose up`. |

## Conventions

- **Currency:** USD (`$`). On-chain = USDC.
- **Numbers:** `1000` → `1K`, `1000000` → `1M`.
- **Secrets:** never in repo. `.env.example` with placeholders, real `.env` gitignored.
- **Networking:** localhost only, every service exposes `/health` + `/status`.
- **Commits:** Conventional Commits.

## Glossary

- **ALICE:** Autonomous AI agent framework — task execution, tool routing, chain sync.
- **alice-general:** Worker node that receives and processes tasks from the coordinator service.
- **the coordinator service:** Task coordinator — routes work to workers, manages priorities.
- **THESEED:** L0 blockchain infrastructure (chain 0, Clique PoA).
- **NETHUB:** Isolated browser — zero tracking, zero telemetry.
- **x402:** Micropayment service layer — USDC on Base.
- **Fleet node:** One container running task work as concurrent workers.

## Repository layout

```
How-To-Start/
├── .github/
│   └── workflows/
│       └── doc-lint.yml              # CI: link check, no leaked keys
├── docker/
│   └── alice-general/
│       ├── Dockerfile                # minimum alice-general image
│       ├── docker-compose.yml        # one-command deploy
│       ├── alice_general.py          # task executor (362 lines)
│       ├── entrypoint.sh             # container entry
│       └── .env.example              # env overrides
├── docs/
│   └── alice-general-docker.md       # quickstart guide
├── .env.example
├── .gitignore
└── README.md
```

## CI

`doc-lint` on every push/PR: verifies links resolve and no API keys leaked.

## Status

- `docker/alice-general/`: **RUNNABLE** — `docker compose up -d --build`
- `docs/alice-general-docker.md`: **READY** — full quickstart guide

## Coming soon

- THESEED L0 chain quickstart (geth Clique PoA)
- NETHUB isolated browser deploy
- ALICEHUB centralized hub setup
- MCP tools server quickstart
