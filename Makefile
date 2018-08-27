VENV=venv
COVERAGE=$(VENV)/bin/coverage
PIP=$(VENV)/bin/pip
PYTHON=$(VENV)/bin/python
FLAKE8=$(VENV)/bin/flake8

.PHONY: run
run: venv rulesengine/db.sqlite3
	$(PYTHON) rulesengine/manage.py runserver_plus

.PHONY: check
check: lint test benchmark

.PHONY: benchmark
benchmark: venv clean-db fuzz-large
	cd rulesengine; \
	../$(PYTHON) manage.py benchmark

.PHONY: test
test: runtests coveragereport

.PHONY: runtests
runtests: venv
	cd rulesengine; \
	../$(COVERAGE) run --source=rules --omit="*/migrations/*,*/admin.py,*/apps.py,*/test_*" ./manage.py test

.PHONY: coveragereport
coveragereport:
	cd rulesengine; \
	../$(COVERAGE) report -m --skip-covered; \
	rm -f .coverage

.PHONY: lint
lint: venv
	$(FLAKE8) rulesengine --exclude migrations,settings.py

rulesengine/db.sqlite3: venv
	cd rulesengine; \
	../$(PYTHON) manage.py migrate;

.PHONY: fuzz-large
fuzz-large: rulesengine/db.sqlite3
	cd rulesengine; \
	../$(PYTHON) manage.py loaddata rules/fixtures/fuzzed-large.json

.PHONY: fuzz-small
fuzz-small:
	cd rulesengine; \
	../$(PYTHON) manage.py loaddata rules/fixtures/fuzzed-large.json

venv:
	virtualenv --python `which python3` venv
	$(PIP) install git+https://github.com/dignio/ultrajson.git
	$(PIP) install -r requirements.txt

.PHONY: clean
clean: clean-db clean-files

.PHONY: clean-db
clean-db:
	rm -rf rulesengine/db.sqlite3

.PHONY: clean-files
clean-files:
	rm -rf venv
	find rulesengine/ -name __pycache__ -or -name "*.py[co]" -exec rm -rf {} \;
