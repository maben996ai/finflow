.PHONY: dev dev-build down down-v logs ps build clean

COMPOSE = docker compose

dev:
	$(COMPOSE) up

dev-build:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

down-v:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

build:
	$(COMPOSE) build

clean:
	$(COMPOSE) down -v --rmi local
