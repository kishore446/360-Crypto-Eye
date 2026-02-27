#!/usr/bin/env bash
set -euo pipefail
COMPOSE_FILE="infra/docker/docker-compose.yml"

docker compose -f "$COMPOSE_FILE" ps
for svc in publisher ops-bot; do
  docker compose -f "$COMPOSE_FILE" ps "$svc" | grep -q "Up" || { echo "ERROR: $svc not Up"; exit 1; }
done
echo "Smoke test passed."
