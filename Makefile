# Developer entry points for breezy-roleplay.
#
# Every target is runnable from a clean checkout. CI calls the same commands,
# so "green locally" and "green in CI" mean the same thing.

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
PY := $(BIN)/python
PIP := $(BIN)/pip
NPM ?= npm

.DEFAULT_GOAL := help

.PHONY: help setup install lint format format-check type test coverage demo smoke \
        quality docs security changelog workflows ruleset ruleset-dry-run check clean

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

$(PY):
	$(PYTHON) -m venv $(VENV)

setup: $(PY) ## Create the virtualenv, install dependencies, install git hooks
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	$(BIN)/pre-commit install --install-hooks
	$(NPM) ci

install: setup ## Alias for setup

lint: ## Run Ruff's linter
	$(BIN)/ruff check src tests scripts

format: ## Apply Ruff formatting
	$(BIN)/ruff format src tests scripts

format-check: ## Verify formatting without changing files
	$(BIN)/ruff format --check src tests scripts

type: ## Run mypy in strict mode
	$(BIN)/mypy src tests

test: ## Run the test suite in parallel
	$(BIN)/pytest -n auto

coverage: ## Run tests with branch coverage and the configured threshold
	$(BIN)/pytest --cov=breezy_roleplay --cov-report=term-missing --cov-report=xml

demo: ## Create and archive a demonstration session
	PYTHONPATH=src $(PYTHON) -m breezy_roleplay demo

smoke: ## Run the end-to-end CLI smoke test in a scratch directory
	bash scripts/smoke_test.sh

quality: ## Repository hygiene checks (size, complexity, TODOs, dead code, duplication)
	bash scripts/check_large_files.sh
	bash scripts/check_complexity.sh
	bash scripts/check_todos.sh
	$(BIN)/vulture src
	$(BIN)/deptry src
	$(NPM) exec --no -- jscpd --config .jscpd.json .

docs: ## Regenerate the scenario index from scenarios/*.md
	bash scripts/generate_scenario_index.sh

security: ## Run the local Semgrep security review
	bash scripts/security_review.sh

changelog: ## Regenerate CHANGELOG.md from Conventional Commits
	$(BIN)/pip install --quiet "git-cliff==2.14.2"
	$(BIN)/git-cliff --config cliff.toml --unreleased --prepend CHANGELOG.md

workflows: ## Validate workflow files with actionlint
	docker run --rm -v "$(CURDIR):/repo" -w /repo rhysd/actionlint:1.7.12

ruleset: ## Apply .github/rulesets/main.json to the repository (requires admin)
	python3 scripts/apply_ruleset.py

ruleset-dry-run: ## Print the branch ruleset payload without applying it
	python3 scripts/apply_ruleset.py --dry-run

check: lint format-check type coverage quality docs ## Everything CI runs
	git diff --exit-code docs/scenarios.md

clean: ## Remove local caches and build output
	rm -rf $(VENV)/.cache .pytest_cache .mypy_cache .ruff_cache .coverage \
		coverage.xml junit.xml build dist src/*.egg-info reports
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
