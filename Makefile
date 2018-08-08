.PHONY: run
run: venv
	venv/bin/python rulesengine/manage.py runserver_plus

.PHONY: check
check: test lint

.PHONY: test
test: venv
	cd rulesengine; \
	../venv/bin/coverage run --source=rules --omit="*/migrations/*,*/admin.py,*/apps.py" ./manage.py test; \
	../venv/bin/coverage report -m --skip-covered; \
	rm .coverage

.PHONY: lint
lint: venv
	venv/bin/flake8 rulesengine --exclude migrations,settings.py

venv:
	virtualenv --python `which python3` venv
	venv/bin/pip install -r requirements.txt

.PHONY: clean
clean:
	rm -rf venv
