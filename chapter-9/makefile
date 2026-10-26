.PHONY: db-up db-down db-logs db-status

COMPOSE_FILE = qdrant-neo4j-docker-compose.yml

# Start Qdrant and Neo4j containers
db-up:
	@echo "==> Starting Qdrant and Neo4j Docker containers..."
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "==> Qdrant & Neo4j are up and running!"
	@echo "    - Qdrant Web UI: http://localhost:6333/dashboard"
	@echo "    - Neo4j Web UI:  http://localhost:7474"

# Stop Qdrant and Neo4j containers
db-down:
	@echo "==> Stopping Docker containers..."
	docker compose -f $(COMPOSE_FILE) down
	@echo "==> Containers stopped."

# View live logs for both or specific containers
db-logs:
	docker compose -f $(COMPOSE_FILE) logs -f

# Check container status
db-status:
	docker compose -f $(COMPOSE_FILE) ps
