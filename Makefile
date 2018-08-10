.PHONY: run
run: venv rulesengine/db.sqlite3
	venv/bin/python rulesengine/manage.py runserver_plus

rulesengine/db.sqlite3:
	cd rulesengine && ../venv/bin/python manage.py migrate

.PHONY: check
check: test lint

.PHONY: test
test: runtests coveragereport

.PHONY: runtests
runtests: venv
	cd rulesengine; \
	../venv/bin/coverage run --source=rules --omit="*/migrations/*,*/admin.py,*/apps.py" ./manage.py test

.PHONY: coveragereport
coveragereport:
	cd rulesengine; \
	../venv/bin/coverage report -m --skip-covered; \
	rm -f .coverage

.PHONY: lint
lint: venv
	venv/bin/flake8 rulesengine --exclude migrations,settings.py

venv:
	virtualenv --python `which python3` venv
	venv/bin/pip install --index-url https://devpi.archive.org/ait/packages/+simple/ -r requirements.txt

.PHONY: clean
clean:
	rm -rf venv
	find rulesengine/ -name __pycache__ -or -name "*.py[co]" -exec rm -rf {} \;
