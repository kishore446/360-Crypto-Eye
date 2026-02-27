# 360-Crypto-Eye

## Run on VPS
```bash
cd /opt/360-crypto-eye
docker compose -f infra/docker/docker-compose.yml up -d --build
```

## Check status
```bash
docker compose -f infra/docker/docker-compose.yml ps
docker compose -f infra/docker/docker-compose.yml logs --tail=100 publisher
docker compose -f infra/docker/docker-compose.yml logs --tail=100 ops-bot
```
