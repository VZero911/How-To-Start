#!/bin/bash
set -e
echo "◈ ALICE GENERAL — Starting on port ${ALICE_PORT}"
echo "  Role: ${ALICE_ROLE}"
echo "  DASHBOARD: ${DASHBOARD_HOST}:${DASHBOARD_PORT}"
echo "  Master: ${COORDINATOR_HOST}:${COORDINATOR_PORT}"
exec python3 -u alice_general.py
