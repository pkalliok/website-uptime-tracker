
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
        auto_offset_reset='earliest',
        **kafka_credentials
    )

def setUpModule():
    run_mock_service_in_background()
    set_up_kafka_consumer()

def test_working_site(): pass

