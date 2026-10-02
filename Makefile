PYTHON = python3
ENTRY_POINT = a_maze_ing.py
CONFIG = config.txt

all: run

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(ENTRY_POINT) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(ENTRY_POINT) $(CONFIG)

cleean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict