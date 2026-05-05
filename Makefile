.PHONY: install lint test build clean run

PYTHON ?= python3

install:
	$(PYTHON) -m pip install -r requirements-dev.txt
	$(PYTHON) -m pip install -e .

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

test:
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing --cov-report=xml

build:
	$(PYTHON) -m build

clean:
	rm -rf build dist *.egg-info .pytest_cache .coverage coverage.xml htmlcov

run:
	$(PYTHON) -m app.main $(ARGS)
