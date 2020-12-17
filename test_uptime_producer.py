
import requests
from test_mock_web_service import run_mock_service_in_background, change_url
from uptime_producer import report_uptime
from kafka import KafkaConsumer

kafka_cons = None
kafka_credentials = dict(
        bootstrap_servers=open('kafka.host').read(),
        security_protocol='SSL',
        ssl_cafile='kafka.ca',
        ssl_keyfile='kafka.key',
        ssl_certfile='kafka.cert'
)

def set_up_kafka_consumer():
    global kafka_cons
    kafka_cons = KafkaConsumer(
        "uptime",
        group_id='test-consumer',
        **kafka_credentials
    )
    kafka_cons.poll(timeout_ms=1000)

def setUpModule():
    run_mock_service_in_background()
    set_up_kafka_consumer()

def test_working_site():
    assert len(kafka_cons.poll(timeout_ms=1000)) == 0
    report_uptime()
    messages = next(iter(kafka_cons.poll(timeout_ms=1000).values()))
    assert len(messages) == 1

