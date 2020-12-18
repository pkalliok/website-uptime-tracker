
import psycopg2, json
from kafka import KafkaConsumer

def pg_connection(filename):
    return psycopg2.connect(**json.load(open(filename)))

def kafka_connection(bs_host, cafile, keyfile, certfile):
    return KafkaConsumer(
        "uptime",
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
    for event in kafka_consumer: pass
