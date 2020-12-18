
import psycopg2, json, click
from kafka import KafkaConsumer

def pg_connection(filename):
    return psycopg2.connect(**json.load(open(filename)))

def kafka_connection(bs_host, cafile, keyfile, certfile, topic='uptime'):
    return KafkaConsumer(
        topic,
        group_id='uptime-postgresql-persister',
        bootstrap_servers=bs_host,
        security_protocol='SSL',
        ssl_cafile=cafile,
        ssl_keyfile=keyfile,
        ssl_certfile=certfile,
    )

def ensure_event_table(conn):
    with conn:
        with conn.cursor() as curs:
            curs.execute("""
                CREATE TABLE IF NOT EXISTS uptime_events (
                    id SERIAL,
                    time TIMESTAMP NOT NULL DEFAULT now(),
                    url TEXT NOT NULL,
                    http_status INT NOT NULL,
                    delay FLOAT,
                    test_passed INT,
                    UNIQUE(time, url, http_status)
                )""")

def persist_event(conn, event_record):
    with conn:
        with conn.cursor() as curs:
            curs.execute("""
                INSERT INTO uptime_events(url, http_status, delay, test_passed)
                VALUES (%(url)s, %(httpStatus)s, %(delay)s, %(passes)s::INT)
                """, event_record)

def process_events(kafka_consumer, conn):
    for event in kafka_consumer:
        print("got event:", event)
        try:
            message = json.loads(event.value.decode('utf-8'))
            assert isinstance(message['url'], str)
            assert isinstance(message['httpStatus'], int)
            assert isinstance(message['delay'], float)
            assert isinstance(message['passes'], bool)
        except:
            print("malformed message from Kafka:", event.value)
            continue
        persist_event(conn, message)
        kafka_consumer.commit()

@click.command()
@click.argument('kafka-host')
@click.argument('postgres-url')
@click.option('--kafka-key-file', default='kafka.key')
@click.option('--kafka-cert-file', default='kafka.cert')
@click.option('--kafka-ca-file', default='kafka.ca')
@click.option('--kafka-topic', default='uptime')
def run(kafka_host, postgres_url,
            kafka_key_file, kafka_cert_file, kafka_ca_file, kafka_topic):
    process_events(
        kafka_connection(kafka_host, kafka_ca_file, kafka_key_file,
            kafka_cert_file, kafka_topic),
        psycopg2.connect(postgres_url))

if __name__ == '__main__': run()

