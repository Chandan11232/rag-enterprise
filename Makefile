.PHONY: help build up down test lint frontend

help:
	@echo "Makefile commands:"
	@echo "  make build      - Build docker containers"
	@echo "  make up         - Start services with docker-compose"
	@echo "  make down       - Stop services"
	@echo "  make test       - Run pytest unit/integration tests"
	@echo "  make lint       - Run ruff linter"
	@echo "  make frontend   - Run Streamlit frontend dashboard"

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

frontend:
	cd frontend && ../venv/bin/pip install -r requirements.txt && ../venv/bin/streamlit run app.py
