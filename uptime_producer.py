
import click, requests, sys, re
from requests.exceptions import ConnectionError
from time import sleep, perf_counter
from kafka import KafkaProducer
from json import dumps

def make_request(url):
    start = perf_counter()
    try:
        result = requests.get(url)
        code = result.status_code
        content = result.text
    except ConnectionError:
        code = 0
        content = 'Connection refused'
    end = perf_counter()
    return ((end-start), code, content)

def report_uptime(url, check, kafka, kafka_topic):
    time, status, body = make_request(url)
    message = dumps(dict(delay=time, httpStatus=status, passes=check(body)))
    if kafka: kafka.send(kafka_topic, message.encode('utf-8'))
    print('Check status:', status, 'in', time, 's')

def kafka_connection(kafka_host, kafka_key_file,
        kafka_cert_file, kafka_ca_file):
    return KafkaProducer(
            bootstrap_servers=kafka_host,
            security_protocol='SSL',
            ssl_cafile=kafka_ca_file,
            ssl_keyfile=kafka_key_file,
            ssl_certfile=kafka_cert_file
    )

@click.command()
@click.argument('url')
@click.option('--check-pattern', default=None)
@click.option('--check-interval', type=int, show_default=True, default=60)
@click.option('--kafka-host', default=None)
@click.option('--kafka-key-file', default='kafka.key')
@click.option('--kafka-cert-file', default='kafka.cert')
@click.option('--kafka-ca-file', default='kafka.ca')
@click.option('--kafka-topic', default='uptime')
def loop(url, check_pattern, check_interval, kafka_topic, **kwargs):
    kafka = kafka_connection(**kwargs) if kwargs['kafka_host'] else None
    if check_pattern:
        check_re = re.compile(check_pattern)
        check = lambda body: bool(check_re.match(body))
    else: check = lambda body: len(body)
    while True:
        try: report_uptime(url, check, kafka, kafka_topic)
        except:
            print('Got uncaught exception:')
            print(sys.exc_info()[1])
        sleep(check_interval)

if __name__ == '__main__': loop()

