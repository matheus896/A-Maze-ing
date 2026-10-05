PYTHON = python3
ENTRY_POINT = a_maze_ing.py
CONFIG = config.txt
LINT_EXCLUDE = .venv,.git,__pycache__,.mypy_cache,.pytest_cache

.PHONY: all install run debug clean lint lint-strict

all: run

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install pytest flake8 mypy

run:
	$(PYTHON) $(ENTRY_POINT) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(ENTRY_POINT) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

lint:
	flake8 . --exclude=$(LINT_EXCLUDE)
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . --exclude=$(LINT_EXCLUDE)
	mypy . --strict
