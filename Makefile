.PHONY: help build up down test lint ingest

help:
	@echo "Makefile commands:"
	@echo "  make build      - Build docker containers"
	@echo "  make up         - Start services with docker-compose"
	@echo "  make down       - Stop services"
	@echo "  make test       - Run pytest unit/integration tests"
	@echo "  make lint       - Run ruff linter"
	@echo "  make pull-model - Pull DeepSeek-Coder-V2 16b inside Ollama container"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

test:
	pytest -v

lint:
	ruff check .

pull-model:
	docker exec -it rag-enterprise-engine-ollama-1 ollama run deepseek-coder-v2:16b
