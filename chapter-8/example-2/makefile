.PHONY: mongodb-up mongodb-down mongodb-logs

# Start MongoDB and Mongo Express with permission fixes
mongodb-up:
# 	@echo "==> Creating data directory and setting permissions..."
# 	@mkdir -p ./data/mongo_data
# 	@sudo chmod -R 777 ./data/mongo_data
	@echo "==> Starting Docker containers..."
	docker compose -f mongo-docker-compose.yml up -d
	@echo "==> MongoDB is up and running!"

# Stop MongoDB and Mongo Express containers
mongodb-down:
	@echo "==> Stopping Docker containers..."
	docker compose -f mongo-docker-compose.yml down
	@echo "==> Containers stopped."

# View live logs for MongoDB
mongodb-logs:
	docker compose logs -f mongodb