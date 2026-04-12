# FinFlow 开发环境启动脚本
# Mac:     make dev-mac
# Windows: make dev-win  (Git Bash / WSL 中运行)

.PHONY: dev-mac dev-win dev-mac-build dev-win-build down down-v logs ps build clean

COMPOSE_WIN = docker compose -f docker-compose.yml -f docker-compose.win.yml

dev-mac:
	docker compose up

dev-mac-build:
	docker compose up --build

dev-win:
	$(COMPOSE_WIN) up

dev-win-build:
	$(COMPOSE_WIN) up --build

down:
	docker compose down

down-v:
	docker compose down -v

logs:
	docker compose logs -f

ps:
	docker compose ps

build:
	docker compose build

clean:
	docker compose down -v --rmi local
