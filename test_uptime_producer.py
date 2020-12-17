
import requests
from test_mock_web_service import run_mock_service_in_background, \
        change_url, service_url
from uptime_producer import report_uptime
from kafka import KafkaConsumer, KafkaProducer
from json import loads

kafka_cons, kafka_prod = None, None
kafka_credentials = dict(
        bootstrap_servers=open('kafka.host').read(),
        security_protocol='SSL',
        ssl_cafile='kafka.ca',
        ssl_keyfile='kafka.key',
        ssl_certfile='kafka.cert'
)

def set_up_kafka():
    global kafka_cons, kafka_prod
    kafka_prod = KafkaProducer(**kafka_credentials)
    kafka_cons = KafkaConsumer(
        "uptime",
        group_id='test-consumer',
        **kafka_credentials
    )
    kafka_cons.poll(timeout_ms=1000)

def setUpModule():
    run_mock_service_in_background()
    set_up_kafka()

def test_working_site():
    assert len(kafka_cons.poll(timeout_ms=1000)) == 0
    report_uptime(service_url, lambda body: True, kafka_prod, 'uptime')
    messages = next(iter(kafka_cons.poll(timeout_ms=1000).values()))
    assert len(messages) == 1
    msg = loads(messages[0].value.decode('utf-8'))
    assert msg['httpStatus'] == 200
    assert msg['passes'] == True
    assert msg['delay'] < 1

