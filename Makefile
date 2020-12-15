
stamps/install-deps: requirements.txt myenv
	./myenv/bin/pip install -r $<
	touch $@

myenv:
	python3 -m venv myenv
