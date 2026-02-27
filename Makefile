up:
	docker compose -f infra/docker/docker-compose.yml up -d --build

down:
	docker compose -f infra/docker/docker-compose.yml down --remove-orphans

init-db:
	./scripts/init_db.sh

seed-db:
	./scripts/seed_signals.sh

smoke:
	./scripts/smoke_test.sh
