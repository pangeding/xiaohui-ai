# Makefile for Xiaohui AI Elderly Care Platform

.PHONY: help install install-backend install-dev run-demo run-agent format lint test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      Install all production dependencies"
	@echo "  make install-backend    Install backend production dependencies"
	@echo "  make install-dev    Install development dependencies"
	@echo "  make run-demo     Run the backend demo"
	@echo "  make run-agent    Run the agent demo"
	@echo "  make format       Format code with black and ruff"
	@echo "  make lint         Lint code with ruff"
	@echo "  make type-check   Type check with mypy"
	@echo "  make test         Run tests with pytest (if any)"
	@echo "  make clean        Clean up caches and temporary files"

# Install all production dependencies
install: install-backend install-agents

# Install backend production dependencies
install-backend:
	cd backend && uv sync --frozen

# Install agents dependencies
install-agents:
	cd agents && uv sync --frozen

# Install development dependencies
install-dev:
	cd backend && uv sync --frozen --dev
	cd agents && uv sync --frozen --dev

# Run the backend demo
run-demo:
	cd backend && uv run python ../agents/demo.py

# Run the agent demo directly
run-agent:
	cd agents && PYTHONPATH=$(shell pwd):$${PYTHONPATH} uv run python demo.py

dev-agent:
	cd agents && uv run langgraph dev

# Format code
format: format-backend format-agents

format-backend:
	cd backend && uv run black ../agents
	cd backend && uv run ruff check --fix ../agents

format-agents:
	cd agents && uv run black .
	cd agents && uv run ruff check --fix .

# Lint code
lint: lint-backend lint-agents

lint-backend:
	cd backend && uv run ruff check ../agents

lint-agents:
	cd agents && uv run ruff check .

# Type checking
type-check:
	cd backend && uv run mypy ../agents

# Run tests (if any)
test:
	cd backend && uv run pytest -v

# Clean up caches and temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".env" -prune -o -type f -name ".env*.local" -delete 2>/dev/null || true
