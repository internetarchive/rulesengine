VENV=venv
COVERAGE=$(VENV)/bin/coverage
PIP=$(VENV)/bin/pip
PYTHON=$(VENV)/bin/python

.PHONY: run
run: venv rulesengine/db.sqlite3
	$(PYTHON) rulesengine/manage.py runserver_plus

.PHONY: check
check: lint test benchmark

.PHONY: benchmark
benchmark: venv rulesengine/db.sqlite3
	cd rulesengine; \
	../$(PYTHON) manage.py benchmark

.PHONY: test
test: runtests coveragereport

.PHONY: runtests
runtests: venv
	cd rulesengine; \
	../$(COVERAGE) run --source=rules --omit="*/migrations/*,*/admin.py,*/apps.py" ./manage.py test

.PHONY: coveragereport
coveragereport:
	cd rulesengine; \
	../$(COVERAGE) report -m --skip-covered; \
	rm -f .coverage

.PHONY: lint
lint: venv
	venv/bin/flake8 rulesengine --exclude migrations,settings.py

rulesengine/db.sqlite3: venv
	cd rulesengine; \
	../$(PYTHON) manage.py migrate

venv:
	virtualenv --python `which python3` venv
	$(PIP) install git+https://github.com/dignio/ultrajson.git
	$(PIP) install -r requirements.txt

.PHONY: clean
clean:
	rm -rf venv rulesengine/db.sqlite3
	find rulesengine/ -name __pycache__ -or -name "*.py[co]" -exec rm -rf {} \;
