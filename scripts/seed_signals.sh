#!/usr/bin/env bash
set -euo pipefail
cat scripts/seed_signals.sql | docker compose -f infra/docker/docker-compose.yml exec -T db psql -U postgres -d crypto_eye
