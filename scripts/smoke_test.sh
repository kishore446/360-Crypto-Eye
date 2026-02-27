#!/usr/bin/env bash
set -euo pipefail

echo "[1/3] health"
curl -fsS http://localhost:8001/health

echo
echo "[2/3] latest signals"
curl -fsS "http://localhost:8001/signals/latest?limit=1"

echo
echo "[3/3] container status"
docker compose -f infra/docker/docker-compose.yml ps
