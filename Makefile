
AIVEN_ACCOUNT = panu.kalliokoski@sange.fi
KAFKA_SERVICE_NAME = uptime-test-kafka
PG_SERVICE_NAME = uptime-test-postgres

.PHONY: test
test: stamps/run-tests

stamps/run-tests: $(wildcard *.py) stamps/install-deps
	./myenv/bin/nose2

stamps/setup-postgres: stamps/aiven-login
	./myenv/bin/avn service create -p startup-4 -t pg $(PG_SERVICE_NAME)
	./myenv/bin/avn service wait $(PG_SERVICE_NAME)
	./myenv/bin/avn service user-create \
		--username $(PG_SERVICE_NAME)_user $(PG_SERVICE_NAME)
	./myenv/bin/avn service database-create \
		--dbname $(PG_SERVICE_NAME)_db $(PG_SERVICE_NAME)
	touch $@

stamps/kafka-credentials: stamps/setup-kafka
	./myenv/bin/avn service get --json $(KAFKA_SERVICE_NAME) \
	| jq '.users|map(select(.username=="$(KAFKA_SERVICE_NAME)_user"))|.[]' \
	> $@

stamps/setup-kafka: stamps/aiven-login
	./myenv/bin/avn service create -p startup-2 -t kafka \
		$(KAFKA_SERVICE_NAME)
	./myenv/bin/avn service wait $(KAFKA_SERVICE_NAME)
	./myenv/bin/avn service user-create \
		--username $(KAFKA_SERVICE_NAME)_user $(KAFKA_SERVICE_NAME)
	./myenv/bin/avn service topic-create \
		--partitions 1 --replication 2 $(KAFKA_SERVICE_NAME) uptime
	touch $@

stamps/aiven-login: stamps/install-deps
	./myenv/bin/avn user login $(AIVEN_ACCOUNT)
	touch $@

.PHONY: try-mock
try-mock: stamps/install-deps
	FLASK_APP=mock_web_service.py ./myenv/bin/flask run

stamps/install-deps: requirements.txt myenv
	./myenv/bin/pip install -r $<
	touch $@

myenv:
	python3 -m venv myenv

