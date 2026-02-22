# Garmin Dashboard Makefile

.PHONY: install dev dev-backend dev-frontend test test-backend test-frontend lint format build prod

# --- Setup ---
install:
	@echo "Installing dependencies..."
	uv sync
	cd frontend && bun install

# --- Development ---
dev:
	@echo "Starting backend and frontend in development mode..."
	make -j 2 dev-backend dev-frontend

dev-backend:
	@echo "Starting FastAPI backend..."
	uv run --env-file .env python main.py

dev-frontend:
	@echo "Starting Nuxt 4 frontend..."
	cd frontend && bun run dev | tee -a ../frontend.log

# --- Testing ---
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	PYTHONPATH=. uv run pytest --cov=garmin_dashboard --cov=main

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && bun run test:coverage

# --- Quality ---
lint:
	@echo "Linting backend..."
	uv run ruff check .
	@echo "Linting frontend..."
	cd frontend && bun run lint

format:
	@echo "Formatting backend..."
	uv run ruff format .
	@echo "Formatting frontend..."
	cd frontend && bun run format

# --- Build & Production ---
build:
	@echo "Building frontend..."
	cd frontend && bun run build

prod: build
	@echo "Starting production environment..."
	# In a real setup, you might use a process manager like pm2 or docker-compose here.
	@echo "Backend: uv run uvicorn main:app --host 0.0.0.0 --port 8000"
	@echo "Frontend: node frontend/.output/server/index.mjs"
