.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## Build project
	poetry self update
	poetry lock --no-update
	poetry install --sync --no-root
	poetry run pre-commit install

.PHONY: dead-code
dead-code:
	poetry run vulture ./notifications_utils --min-confidence=100

.PHONY: test
test: ## Run tests
	poetry run black .
	poetry run flake8 .
	poetry run isort --check-only ./notifications_utils ./tests
	poetry run pytest -n4 --maxfail=10

.PHONY: test-with-coverage
test-with-coverage: ## Run tests with coverage
	poetry run black .
	poetry run flake8 .
	poetry run isort --check-only ./notifications_utils ./tests
	poetry run coverage run -m pytest -n4 --maxfail=10
	poetry run coverage report -m --fail-under=95
	poetry run coverage html -d .coverage_cache

.PHONY: avg-complexity
avg-complexity:
	echo "*** Shows average complexity in radon of all code ***"
	poetry run radon cc ./notifications_utils -a -na

.PHONY: too-complex
too-complex:
	echo "*** Shows code that got a rating of C, D or F in radon ***"
	poetry run radon cc ./notifications_utils -a -nc

.PHONY: clean
clean:
	rm -rf cache target venv .coverage build tests/.cache

.PHONY: fix-imports
fix-imports:
	poetry run isort ./notifications_utils ./tests

.PHONY: audit
audit:
	poetry requirements > requirements.txt
	poetry requirements --dev > requirements_for_test.txt
	poetry run pip-audit -r requirements.txt
	-poetry run pip-audit -r requirements_for_test.txt

.PHONY: py-lock
py-lock: ## Syncs dependencies and updates lock file without performing recursive internal updates
	poetry lock --no-update
	poetry install --sync --no-root

.PHONY: freeze-requirements
freeze-requirements: ## Pin all requirements including sub dependencies into requirements.txt
	poetry export --without-hashes --format=requirements.txt > requirements.txt

.PHONY: static-scan
static-scan:
	poetry run bandit -r app/
