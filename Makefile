.PHONY: help format format-check lint test

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

format:  ## Format code with black and isort
	@echo "Formatting Python code..."
	python -m black .
	python -m isort .
	@echo "Formatting frontend code..."
	cd frontend && npm run format

format-check:  ## Check code formatting
	@echo "Checking Python code formatting..."
	python -m black --check .
	python -m isort --check-only .
	@echo "Checking frontend code formatting..."
	cd frontend && npm run format:check

lint:  ## Run linters
	@echo "Running Python linters..."
	python -m black --check .
	python -m isort --check-only .
	python -m mypy src/ --ignore-missing-imports
	@echo "Running frontend linters..."
	cd frontend && npm run lint

test:  ## Run tests
	@echo "Running backend tests..."
	pytest --cov=src/gaiarouter --cov-report=term
	@echo "Running frontend tests..."
	cd frontend && npm run test:unit
