# ALICE GENERAL — Docker Quickstart

Minimum Docker setup to run one **alice-general** worker node.

## What it does

`alice-general` is a task executor. It:

1. Connects to **the coordinator service** (task coordinator) and **dashboard** (dashboard service).
2. Receives tasks — code review, DeFi scanning, system health checks.
3. Processes tasks via the x402 service layer or delegation server.
4. Reports completion back to COORDINATOR.
5. Self-generates tasks when idle (marketplace scans, chain monitoring).

The node does **not** call a model directly. It delegates to upstream services.

## Requirements

- Docker and Docker Compose
- A running the coordinator service on the same machine (or reachable network)
- A running dashboard server on the same machine (or reachable network)

## Quick start

```bash
cd docker/alice-general
cp .env.example .env          # edit if COORDINATOR runs on a different host
docker compose up -d --build
```

Verify:

```bash
curl http://localhost:8080/health
# {"status":"ok"}

curl http://localhost:8080/status
# full node status JSON
```

## Endpoints

| Route | Method | What |
|-------|--------|------|
| `/health` | GET | Liveness probe — `{"status":"ok"}` |
| `/status` | GET | Full node state: connections, task counts, uptime |
| `/config` | GET | Current node config + feature list |
| `/task` | POST | Submit a task `{"type":"...", "input":"..."}` |
| `/complete` | POST | Report task completion (from upstream) |

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `ALICE_ROLE` | `GENERAL` | Node role identifier |
| `ALICE_PORT` | `8080` | HTTP port |
| `DASHBOARD_HOST` | `localhost` | dashboard server host |
| `DASHBOARD_PORT` | `8083` | dashboard server port |
| `COORDINATOR_HOST` | `localhost` | the coordinator service host |
| `COORDINATOR_PORT` | `8082` | the coordinator service port |
| `X402_HOST` | `localhost` | x402 service host |
| `X402_PORT` | `8084` | x402 service port |

## Architecture

```
┌─────────────────────────────────┐
│         the coordinator service            │
│    (task coordinator :8082)     │
└──────────┬──────────────────────┘
           │  tasks ↓  results ↑
┌──────────▼──────────────────────┐
│       alice-general             │
│    (worker node :8080)          │
│                                 │
│  connectivity_loop  ←→  DASHBOARD     │
│  worker_loop        ←→  COORDINATOR │
│  self_task_loop     →  tasks   │
└─────────────────────────────────┘
           │
    ┌──────▼──────┐
    │  x402 / DLG │
    │  (upstream)  │
    └─────────────┘
```

## Scale

To run multiple workers:

```bash
# Worker 1 on port 8080 (default)
ALICE_PORT=8080 docker compose up -d --build

# Worker 2 on port 8081
ALICE_PORT=8081 docker compose -p alice-general-2 up -d --build
```

## Security

- Binds to `localhost` only — no network exposure.
- `no-new-privileges` Docker security opt.
- No secrets, no API keys, no model calls.
- No secrets or privileged endpoints are exposed.
