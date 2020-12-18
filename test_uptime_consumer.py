
from test_uptime_producer import kafka_prod, set_up_kafka
from json import dumps, loads
import psycopg2

pg_conn = None

def set_up_postgres():
    global pg_conn
    if pg_conn: return
    pg_conn = psycopg2.connect(**loads(open("pg-creds.json").read()))

def setUpModule():
    #set_up_kafka()
    set_up_postgres()
