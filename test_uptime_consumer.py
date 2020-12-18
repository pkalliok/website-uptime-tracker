
from uptime_consumer import process_events, persist_event
from test_uptime_producer import kafka_prod, set_up_kafka
from json import dumps, loads
import psycopg2

pg_conn = None

def set_up_postgres():
    global pg_conn
    if pg_conn: return
    pg_conn = psycopg2.connect(**loads(open("pg-creds.json").read()))

def sql_query(query, args=None):
    with pg_conn:
        with pg_conn.cursor() as curs:
            if args: curs.execute(query, args)
            else:
                curs.execute(query)
                return curs.fetchall()

def setUpModule():
    set_up_kafka()
    set_up_postgres()

def test_message_is_persisted():
    ((max_id,),) = sql_query("select max(id) from uptime_events")
    persist_event(dict(url="foo", httpStatus="200", body=""))
    ((url, status, body),) = sql_query("""
        select url, http_status, body
        from uptime_events
        where id > %s""", (max_id,))
    assert url == 'foo'
    assert status == 200
    assert body == ''

