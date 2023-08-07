.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## Build project
	pip install -r requirements_for_test.txt

.PHONY: test
test: ## Run tests
	flake8 .
	isort --check-only ./notifications_utils ./tests
	pytest -n4
	python setup.py sdist


.PHONY: avg-complexity
avg-complexity:
	echo "*** Shows average complexity in radon of all code ***"
	pipenv run radon cc ./notifications_utils -a -na

.PHONY: too-complex
too-complex:
	echo "*** Shows code that got a rating of C, D or F in radon ***"
	pipenv run radon cc ./notifications_utils -a -nc


clean:
	rm -rf cache venv

.PHONY: fix-imports
fix-imports:
	isort ./notifications_utils ./tests

.PHONY: audit
audit:
	pip install --upgrade pip-audit
	pip-audit -r requirements.txt
	-pip-audit -r requirements_for_test.txt

.PHONY: freeze-requirements
freeze-requirements: ## Pin all requirements including sub dependencies into requirements.txt
	pip install --upgrade pip-tools
	pip-compile requirements.in

.PHONY: static-scan
static-scan:
	pip install --upgrade bandit
	bandit -r notifications_utils/

.PHONY: reset-version
reset-version:
	git fetch
	git checkout origin/main -- notifications_utils/version.py

.PHONY: version-major
version-major: reset-version ## Update the major version number
	./scripts/bump_version.py major

.PHONY: version-minor
version-minor: reset-version ## Update the minor version number
	./scripts/bump_version.py minor

.PHONY: version-patch
version-patch: reset-version ## Update the patch version number
	./scripts/bump_version.py patch
