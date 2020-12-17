
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
    for _ in range(2): kafka_cons.poll(timeout_ms=1000)

def setUpModule():
    run_mock_service_in_background()
    set_up_kafka()

def tearDownModule():
    kafka_cons.commit()

def get_kafka_message():
    messages = next(iter(kafka_cons.poll(timeout_ms=1000).values()))
    assert len(messages) == 1
    return loads(messages[0].value.decode('utf-8'))

def test_working_site():
    assert len(kafka_cons.poll(timeout_ms=1000)) == 0
    report_uptime(service_url, lambda body: True, kafka_prod, 'uptime')
    msg = get_kafka_message()
    assert msg['httpStatus'] == 200
    assert msg['passes'] == True
    assert msg['delay'] < 1

def test_failing_site():
    assert len(kafka_cons.poll(timeout_ms=1000)) == 0
    assert requests.post(change_url, json=dict(code=503, body='sorryy')).json() == 'ok'
    report_uptime(service_url, lambda body: True, kafka_prod, 'uptime')
    msg = get_kafka_message()
    assert msg['httpStatus'] == 503
    assert msg['passes'] == True
    assert msg['delay'] < 1
    assert requests.post(change_url, json=dict(code=200, body='Hello, again')).json() == 'ok'

def test_failing_content():
    assert len(kafka_cons.poll(timeout_ms=1000)) == 0
    assert requests.post(change_url, json=dict(code=200, body='Something went wrong.')).json() == 'ok'
    report_uptime(service_url, lambda body: body.startswith('Hello,'), kafka_prod, 'uptime')
    assert get_kafka_message()['passes'] == False
    assert requests.post(change_url, json=dict(code=200, body='Hello, stranger')).json() == 'ok'
    report_uptime(service_url, lambda body: body.startswith('Hello,'), kafka_prod, 'uptime')
    assert get_kafka_message()['passes'] == True

def test_missing_kafka():
    assert len(kafka_cons.poll(timeout_ms=1000)) == 0
    report_uptime(service_url, lambda body: False, None, 'uptime')
    assert len(kafka_cons.poll(timeout_ms=1000)) == 0

