# Makefile for Xiaohui AI Elderly Care Platform

.PHONY: help install install-dev run-demo format lint test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      Install production dependencies (using poetry)"
	@echo "  make install-dev  Install development dependencies"
	@echo "  make run-demo     Run the agent demo"
	@echo "  make format       Format code with black and ruff"
	@echo "  make lint         Lint code with ruff"
	@echo "  make type-check   Type check with mypy"
	@echo "  make test         Run tests with pytest (if any)"
	@echo "  make clean        Clean up caches and temporary files"

# Install production dependencies
install:
	cd backend && poetry install --only main

# Install development dependencies
install-dev:
	cd backend && poetry install --with dev

# Run the agent demo
run-demo:
	cd backend && poetry run python ../agents/demo.py

# Format code
format:
	cd backend && poetry run black ../agents
	cd backend && poetry run ruff check --fix ../agents

# Lint code
lint:
	cd backend && poetry run ruff check ../agents

# Type checking
type-check:
	cd backend && poetry run mypy ../agents

# Run tests (if any)
test:
	cd backend && poetry run pytest -v

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