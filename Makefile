
.PHONY: test
test: stamps/run-tests

stamps/run-tests: $(wildcard *.py) stamps/install-deps
	./myenv/bin/nose2

.PHONY: try-mock
try-mock: stamps/install-deps
	FLASK_APP=mock_web_service.py ./myenv/bin/flask run

stamps/install-deps: requirements.txt myenv
	./myenv/bin/pip install -r $<
	touch $@

myenv:
	python3 -m venv myenv
