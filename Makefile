venv:
	virtualenv --python `which python3` venv
	venv/bin/pip install -r requirements.txt

.PHONY: clean
clean:
	rm -rf venv
