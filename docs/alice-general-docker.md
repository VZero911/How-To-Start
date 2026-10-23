# ALICE General — Docker Quickstart

Minimum Docker setup to run one **alice-general** worker node.

## What it does

`alice-general` is a task-executor worker. It:

1. Connects to an upstream **coordinator service** (task distribution) and a **dashboard service** (status reporting).
2. Receives tasks — code review, scanning, health checks.
3. Processes them through the upstream service layer.
4. Reports completion back to the coordinator.
5. Self-generates work when idle.

The node does **not** call a model directly — it delegates to upstream services.

## Requirements

- Docker and Docker Compose
- Reachable coordinator and dashboard services (same machine or network)

## Quick start

```bash
cd docker/alice-general
cp .env.example .env      # set the hosts/ports for your own environment
docker compose up -d --build
```

Verify (replace `<host>` and `<port>` with the values from your `.env`):

```bash
curl http://<host>:<port>/health
# {"status":"ok"}

curl http://<host>:<port>/status
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

## Configuration

All settings come from `.env`. No real hosts or ports are published here — supply your own.

| Variable | Description |
|----------|-------------|
| `ALICE_ROLE` | Node role identifier |
| `ALICE_PORT` | HTTP port the node binds |
| `COORDINATOR_HOST` / `COORDINATOR_PORT` | Upstream coordinator service |
| `DASHBOARD_HOST` / `DASHBOARD_PORT` | Dashboard service |
| `X402_HOST` / `X402_PORT` | x402 payment service |

## Scale

Run multiple workers by giving each its own port and Compose project name:

```bash
ALICE_PORT=<port-a> docker compose up -d --build
ALICE_PORT=<port-b> docker compose -p alice-general-2 up -d --build
```

## Security

- Binds to localhost only by default — no public network exposure.
- Runs with the `no-new-privileges` Docker security option.
- No secrets, no API keys, and no model calls in this node.
