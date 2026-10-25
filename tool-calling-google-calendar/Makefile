.PHONY: help build up up-d down restart logs shell status

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build    Build the calendar-assistant Docker image"
	@echo "  up       Run container with live hot reload (foreground)"
	@echo "  up-d     Run container in detached mode (background)"
	@echo "  down     Stop and remove container"
	@echo "  restart  Restart container"
	@echo "  logs     Tail container logs in real time"
	@echo "  shell    Open interactive bash terminal inside container"
	@echo "  status   Check status of containers"

build:
	docker compose -f calendar-tool-docker-compose.yml build

up:
	@echo "==> Starting Docker containers..."
	docker compose -f calendar-tool-docker-compose.yml up
	@echo "==> calendar tool app is up and running!"

up-d:
	@echo "==> Starting Docker containers..."
	docker compose -f calendar-tool-docker-compose.yml up -d
	@echo "==> calendar tool app is up and running!"

down:
	@echo "==> Stopping Docker containers..."
	docker compose -f calendar-tool-docker-compose.yml down
	@echo "==> Containers stopped."

restart: down up

logs:
	docker compose -f calendar-tool-docker-compose.yml logs -f

shell:
	docker compose -f calendar-tool-docker-compose.yml exec calendar-assistant /bin/bash

status:
	docker compose -f calendar-tool-docker-compose.yml ps
