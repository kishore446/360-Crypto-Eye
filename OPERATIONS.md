# Operations Runbook (360-Crypto-Eye)

## Start
cd /opt/360-crypto-eye
docker compose -f infra/docker/docker-compose.yml up -d --build

## Status
docker compose -f infra/docker/docker-compose.yml ps

## Logs
docker compose -f infra/docker/docker-compose.yml logs --tail=100 publisher
docker compose -f infra/docker/docker-compose.yml logs --tail=100 ops-bot

## Restart key services
docker compose -f infra/docker/docker-compose.yml up -d --force-recreate publisher ops-bot

## Stop
docker compose -f infra/docker/docker-compose.yml down
