
from uptime_consumer import process_events, persist_event
from test_uptime_producer import kafka_prod, set_up_kafka
from json import dumps, loads
import psycopg2

pg_conn = None

def sql_query(query, args=None, has_results=True):
    with pg_conn:
        with pg_conn.cursor() as curs:
            if args: curs.execute(query, args)
            else: curs.execute(query)
            if has_results: return curs.fetchall()

def set_up_postgres():
    global pg_conn
    if pg_conn: return
    pg_conn = psycopg2.connect(**loads(open("pg-creds.json").read()))
    ensure_event_table()

def ensure_event_table():
    sql_query("""
        CREATE TABLE IF NOT EXISTS uptime_events (
            id SERIAL,
            time TIMESTAMP NOT NULL DEFAULT now(),
            url TEXT NOT NULL,
            http_status INT NOT NULL,
            delay FLOAT,
            test_passed INT,
            UNIQUE(time, url, http_status)
        )""", has_results=False)

def setUpModule():
    set_up_kafka()
    set_up_postgres()

def test_message_is_persisted():
    ((max_id,),) = sql_query("select max(id) from uptime_events")
    persist_event(pg_conn,
            dict(url="foo", httpStatus="200", delay=0.0, passes=False))
    ((url, status, passed),) = sql_query("""
        select url, http_status, test_passed
        from uptime_events
        where id > %(max_id)s""", dict(max_id=(max_id or 0)))
    assert url == 'foo'
    assert status == 200
    assert not passed

