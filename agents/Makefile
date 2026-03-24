# Makefile for Xiaohui AI Agents

.PHONY: help install install-dev run-demo format lint clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      Install production dependencies (using uv)"
	@echo "  make install-dev  Install development dependencies"
	@echo "  make run-demo     Run the agent demo"
	@echo "  make format       Format code with black and ruff"
	@echo "  make lint         Lint code with ruff"
	@echo "  make clean        Clean up caches and temporary files"

# Install production dependencies
install:
	uv sync --frozen

# Install development dependencies
install-dev:
	uv sync --frozen --dev

# Run the agent demo
run-demo:
	PYTHONPATH=.. uv run python demo.py

# Format code
format:
	uv run black .
	uv run ruff check --fix .

# Lint code
lint:
	uv run ruff check .

# Clean up caches and temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
