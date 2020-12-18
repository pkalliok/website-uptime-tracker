
AIVEN_ACCOUNT = panu.kalliokoski@sange.fi
KAFKA_SERVICE_NAME = uptime-test-kafka
PG_SERVICE_NAME = uptime-test-postgres
CREDENTIALS = kafka.ca kafka.key kafka.cert kafka.host pg-creds.json

.PHONY: test
test: stamps/run-tests

.PHONY: run-test-runner
run-test-runner: stamps/run-tests
	./myenv/bin/nosy

.PHONY: build-images
build-images: stamps/build-producer-image stamps/build-consumer-image

stamps/build-producer-image: uptime_producer.py requirements-run.txt $(CREDENTIALS)
	cp $^ docker-images/
	docker build -t pkalliok:website-uptime-tracker-producer \
		-f docker-images/producer.docker \
		docker-images/
	touch $@

stamps/build-consumer-image: uptime_consumer.py requirements-run.txt $(CREDENTIALS)
	cp $^ docker-images/
	docker build -t pkalliok:website-uptime-tracker-consumer \
		-f docker-images/consumer.docker \
		docker-images/
	touch $@

stamps/run-tests: $(wildcard *.py) stamps/install-deps $(CREDENTIALS)
	./myenv/bin/nose2

kafka.ca: stamps/aiven-login
	./myenv/bin/avn project ca-get --target-filepath $@

kafka.key: stamps/setup-kafka
	jq -r '.connection_info.kafka_access_key' $< > $@

kafka.cert: stamps/setup-kafka
	jq -r '.connection_info.kafka_access_cert' $< > $@

kafka.host: stamps/setup-kafka
	jq -r '.service_uri' $< > $@

pg-creds.json: stamps/setup-postgres
	jq '.connection_info.pg_params[0]' $< \
	| sed 's/defaultdb/$(PG_SERVICE_NAME)_db/' > $@

stamps/setup-postgres: stamps/aiven-login
	./myenv/bin/avn service create -p startup-4 -t pg $(PG_SERVICE_NAME)
	./myenv/bin/avn service wait $(PG_SERVICE_NAME)
	./myenv/bin/avn service database-create \
		--dbname $(PG_SERVICE_NAME)_db $(PG_SERVICE_NAME)
	./myenv/bin/avn service get --json $(PG_SERVICE_NAME) > $@

stamps/setup-kafka: stamps/aiven-login
	./myenv/bin/avn service create -p startup-2 -t kafka \
		$(KAFKA_SERVICE_NAME)
	./myenv/bin/avn service wait $(KAFKA_SERVICE_NAME)
	./myenv/bin/avn service topic-create \
		--partitions 1 --replication 2 $(KAFKA_SERVICE_NAME) uptime
	./myenv/bin/avn service get --json $(KAFKA_SERVICE_NAME) > $@

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

