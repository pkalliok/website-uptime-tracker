
from uptime_consumer import process_events, persist_event, ensure_event_table, \
        pg_connection
from test_uptime_producer import kafka_prod, set_up_kafka
from json import dumps
from threading import Thread
from time import sleep

pg_conn = None
consumer_thread = None

def sql_query(query, args=None, has_results=True):
    with pg_conn:
        with pg_conn.cursor() as curs:
            if args: curs.execute(query, args)
            else: curs.execute(query)
            if has_results: return curs.fetchall()

def set_up_postgres():
    global pg_conn
    if pg_conn: return
    pg_conn = pg_connection("pg-creds.json")
    ensure_event_table(pg_conn)

def run_consumer_in_background():
    global consumer_thread
    if consumer_thread: return
    consumer_thread = Thread(target=process_events)
    consumer_thread.daemon = True
    consumer_thread.start()

def setUpModule():
    set_up_kafka()
    set_up_postgres()
    run_consumer_in_background()

def test_message_is_persisted():
    ((max_id,),) = sql_query("select max(id) from uptime_events")
    persist_event(pg_conn,
            dict(url="foo", httpStatus=200, delay=0.0, passes=False))
    ((url, status, passed),) = sql_query("""
        select url, http_status, test_passed
        from uptime_events
        where id > %(max_id)s""", dict(max_id=(max_id or 0)))
    assert url == 'foo'
    assert status == 200
    assert not passed

