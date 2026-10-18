"""ALICE GENERAL — Task executor node.

Receives tasks from the coordinator service, processes them via x402 service
or delegation server on the host machine. Reports completion back.
Also proactively searches for work: self-generates tasks from
marketplace scanning, THESEED monitoring, and system health checks.

Classification: general — general access
"""

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from aiohttp import web, ClientSession, ClientTimeout

ROLE = os.environ.get("ALICE_ROLE", "GENERAL")
PORT = int(os.environ.get("ALICE_PORT", "8080"))
DASHBOARD_HOST = os.environ.get("DASHBOARD_HOST", "dashboard-service")
DASHBOARD_PORT = int(os.environ.get("DASHBOARD_PORT", "8083"))
COORDINATOR_HOST = os.environ.get("COORDINATOR_HOST", "coordinator")
COORDINATOR_PORT = int(os.environ.get("COORDINATOR_PORT", "8082"))
X402_HOST = os.environ.get("X402_HOST", "localhost")
X402_PORT = int(os.environ.get("X402_PORT", "8084"))
DELEGATION_HOST = os.environ.get("DELEGATION_HOST", "localhost")
DELEGATION_PORT = int(os.environ.get("DELEGATION_PORT", "8085"))

DASHBOARD_URL = f"http://{DASHBOARD_HOST}:{DASHBOARD_PORT}"
COORDINATOR_URL = f"http://{COORDINATOR_HOST}:{COORDINATOR_PORT}"
X402_URL = f"http://{X402_HOST}:{X402_PORT}"
DELEGATION_URL = f"http://{DELEGATION_HOST}:{DELEGATION_PORT}"

AUTO_UPDATE_INTERVAL = 60
CONFIG_VERSION = 0

state = {
    "role": ROLE,
    "started_at": None,
    "hq_connected": False,
    "master_connected": False,
    "x402_connected": False,
    "delegation_connected": False,
    "config_version": CONFIG_VERSION,
    "auto_updates": 0,
    "tasks_received": 0,
    "tasks_done": 0,
    "tasks_failed": 0,
    "tasks_processing": 0,
    "uptime_s": 0,
}

config = {
    "version": CONFIG_VERSION,
    "auto_update": True,
    "scan_interval": 30,
    "report_interval": 60,
    "features": ["status", "tasks", "health", "config", "execute"],
}

task_inbox: list[dict] = []
task_done: list[dict] = []


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


async def connectivity_loop(app: web.Application) -> None:
    """Check DASHBOARD, COORDINATOR, x402 service, and delegation server connectivity."""
    while True:
        # DASHBOARD
        try:
            async with app["session"].get(
                f"{DASHBOARD_URL}/api/status", timeout=ClientTimeout(total=5)
            ) as resp:
                state["hq_connected"] = resp.status == 200
        except Exception:
            state["hq_connected"] = False

        # COORDINATOR
        try:
            async with app["session"].get(
                f"{COORDINATOR_URL}/status", timeout=ClientTimeout(total=5)
            ) as resp:
                state["master_connected"] = resp.status == 200
        except Exception:
            state["master_connected"] = False

        # x402 service
        try:
            async with app["session"].get(
                f"{X402_URL}/status", timeout=ClientTimeout(total=5)
            ) as resp:
                state["x402_connected"] = resp.status == 200
        except Exception:
            state["x402_connected"] = False

        # Delegation server
        try:
            async with app["session"].get(
                f"{DELEGATION_URL}/status", timeout=ClientTimeout(total=5)
            ) as resp:
                state["delegation_connected"] = resp.status == 200
        except Exception:
            state["delegation_connected"] = False

        await asyncio.sleep(AUTO_UPDATE_INTERVAL)


async def worker_loop(app: web.Application) -> None:
    """Process received tasks — execute via delegation server or x402."""
    while True:
        for task in list(task_inbox):
            if task["status"] != "RECEIVED":
                continue

            task["status"] = "PROCESSING"
            state["tasks_processing"] += 1
            master_task_id = task.get("master_task_id")

            try:
                result = await process_task(app, task)
                task["status"] = "DONE"
                task["completed_at"] = _ts()
                task["result"] = result
                state["tasks_done"] += 1
                state["tasks_processing"] -= 1

                # Report back to master
                if master_task_id and state["master_connected"]:
                    try:
                        async with app["session"].post(
                            f"{COORDINATOR_URL}/tasks/complete",
                            json={"task_id": master_task_id, "result": result},
                            timeout=ClientTimeout(total=10),
                        ) as resp:
                            pass
                    except Exception:
                        pass

                task_done.append(task)
                task_inbox.remove(task)

            except Exception as e:
                task["status"] = "FAILED"
                task["error"] = str(e)
                state["tasks_failed"] += 1
                state["tasks_processing"] -= 1

                task_done.append(task)
                task_inbox.remove(task)

        await asyncio.sleep(1)


async def process_task(app: web.Application, task: dict) -> dict:
    """Route task to the best execution backend."""
    task_data = task.get("task", {})
    task_type = task_data.get("type", "execute")
    task_input = task_data.get("input", task_data.get("content", str(task_data)))

    # Try delegation server first (has routing logic)
    if state["delegation_connected"]:
        try:
            async with app["session"].post(
                f"{DELEGATION_URL}/delegate",
                json={"type": task_type, "input": task_input},
                timeout=ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("status") == "COMPLETED":
                        return {"source": "delegation-server", "result": data.get("result")}
        except Exception:
            pass

    # Try x402 dev mode (free, no payment)
    if state["x402_connected"]:
        module_map = {
            "execute": "execute",
            "analyze": "analyze",
            "review": "review",
            "debug": "debug",
            "query": "query",
            "audit": "audit",
            "defi-scan": "defi-scan",
        }
        module = module_map.get(task_type, "query")
        try:
            async with app["session"].post(
                f"{X402_URL}/dev/module/{module}",
                json={"input": task_input},
                timeout=ClientTimeout(total=60),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"source": "x402-dev", "module": module, "result": data.get("result")}
        except Exception:
            pass

    return {"source": "local", "result": f"Task received: {task_type}", "note": "No execution backend available"}


SELF_TASK_INTERVAL = 120
SELF_TASK_TYPES = [
    {"type": "defi-scan", "input": "Scan Base L2 for new yield opportunities, arb gaps, and liquidation targets. Report any opportunity above 0.5% spread.", "priority": "HIGH"},
    {"type": "analyze", "input": "Check THESEED L0 chain 31337 health: block production, contract deployments, gas usage, validator status.", "priority": "HIGH"},
    {"type": "query", "input": "Scan agent marketplaces (x402, Dealwork.ai, Olas) for new task requests matching ALICE capabilities.", "priority": "MEDIUM"},
    {"type": "audit", "input": "Run security health check: port scan localhost, verify all services bound to localhost, check for open endpoints.", "priority": "HIGH"},
    {"type": "query", "input": "Check system resource usage: CPU, RAM, disk, GPU. Flag anything above 90% utilization.", "priority": "LOW"},
]


async def self_task_loop(app: web.Application) -> None:
    """Proactively generate and execute tasks — ALICE doesn't wait."""
    await asyncio.sleep(30)
    task_index = 0
    while True:
        if state["tasks_processing"] > 2:
            await asyncio.sleep(10)
            continue

        task_def = SELF_TASK_TYPES[task_index % len(SELF_TASK_TYPES)]
        task_index += 1

        entry = {
            "id": f"self-{task_index:04d}",
            "task": task_def,
            "from": "SELF",
            "master_task_id": None,
            "status": "RECEIVED",
            "received_at": _ts(),
            "self_generated": True,
        }
        task_inbox.append(entry)
        state["tasks_received"] += 1

        await asyncio.sleep(SELF_TASK_INTERVAL)


async def uptime_loop(app: web.Application) -> None:
    start = time.monotonic()
    while True:
        state["uptime_s"] = int(time.monotonic() - start)
        await asyncio.sleep(5)


async def handle_status(request: web.Request) -> web.Response:
    return web.json_response({
        **state,
        "timestamp": _ts(),
        "port": PORT,
        "hq": DASHBOARD_URL,
        "master": COORDINATOR_URL,
        "x402": X402_URL,
        "delegation": DELEGATION_URL,
        "config": config,
        "inbox_size": len(task_inbox),
        "done_count": len(task_done),
    })


async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({"status": "OK", "role": ROLE, "uptime": state["uptime_s"]})


async def handle_config(request: web.Request) -> web.Response:
    if request.method == "GET":
        return web.json_response(config)
    data = await request.json()
    for k, v in data.items():
        if k in config and k != "version":
            config[k] = v
    config["version"] += 1
    state["config_version"] = config["version"]
    state["auto_updates"] += 1
    return web.json_response({"status": "UPDATED", "config": config})


async def handle_task(request: web.Request) -> web.Response:
    data = await request.json()
    entry = {
        "id": f"gen-{len(task_inbox) + len(task_done) + 1:04d}",
        "task": data.get("task", {}),
        "from": data.get("from", "unknown"),
        "master_task_id": data.get("master_task_id"),
        "status": "RECEIVED",
        "received_at": _ts(),
    }
    task_inbox.append(entry)
    state["tasks_received"] += 1
    return web.json_response({"status": "RECEIVED", "task": entry})


async def handle_complete(request: web.Request) -> web.Response:
    data = await request.json()
    task_id = data.get("task_id")
    for i, t in enumerate(task_inbox):
        if t["id"] == task_id:
            t["status"] = "DONE"
            t["completed_at"] = _ts()
            t["result"] = data.get("result")
            task_done.append(task_inbox.pop(i))
            state["tasks_done"] += 1
            return web.json_response({"status": "OK", "task": t})
    return web.json_response({"error": "not found"}, status=404)


async def on_startup(app: web.Application) -> None:
    app["session"] = ClientSession(timeout=ClientTimeout(total=10))
    state["started_at"] = _ts()
    app["bg"] = [
        asyncio.create_task(connectivity_loop(app)),
        asyncio.create_task(worker_loop(app)),
        asyncio.create_task(uptime_loop(app)),
        asyncio.create_task(self_task_loop(app)),
    ]
    print(f"◈ ALICE GENERAL — ONLINE")
    print(f"  Port: {PORT} | DASHBOARD: {DASHBOARD_URL} | Master: {COORDINATOR_URL}")
    print(f"  x402: {X402_URL} | Delegation: {DELEGATION_URL}")
    print(f"  Worker: auto-process tasks")
    print(f"  Self-tasking: every {SELF_TASK_INTERVAL}s ({len(SELF_TASK_TYPES)} task types)")
    print(f"  Auto-update: every {AUTO_UPDATE_INTERVAL}s")


async def on_cleanup(app: web.Application) -> None:
    for t in app.get("bg", []):
        t.cancel()
    s = app.get("session")
    if s:
        await s.close()


@web.middleware
async def cors_middleware(request, handler):
    if request.method == 'OPTIONS':
        resp = web.Response(status=204)
    else:
        resp = await handler(request)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp


def create_app() -> web.Application:
    app = web.Application(middlewares=[cors_middleware])
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.router.add_get("/status", handle_status)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/config", handle_config)
    app.router.add_post("/config", handle_config)
    app.router.add_post("/task", handle_task)
    app.router.add_post("/task/complete", handle_complete)
    return app


if __name__ == "__main__":
    bind = "localhost"
    web.run_app(create_app(), host=bind, port=PORT, print=None)
