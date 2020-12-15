
import requests

mock_thread = None
service_url = 'http://localhost:5000/service'

def setUpModule():
    from mock_web_service import mock
    from threading import Thread
    from time import sleep
    mock_thread = Thread(target=mock.run)
    mock_thread.daemon = True
    mock_thread.start()
    sleep(1) # simplest way to give the dev server time to start

def test_default_response():
    assert requests.get(service_url).text.startswith('Hello,')

