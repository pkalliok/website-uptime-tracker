
def persist_event(conn, event_record):
    with conn:
        with conn.cursor() as curs:
            curs.execute("""
                INSERT INTO uptime_events(url, http_status, delay, test_passed)
                VALUES (%(url)s, %(httpStatus)s, %(delay)s, %(passes)s::INT)
                """, event_record)

def process_events(): pass
