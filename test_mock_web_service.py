
import requests

port = 5000
base_url = 'http://localhost:{}/'.format(port)
service_url = base_url + 'service'
change_url = base_url + 'changeResponse'

def setUpModule():
    from mock_web_service import mock
    from threading import Thread
    from time import sleep
    t = Thread(target=mock.run)
    t.daemon = True
    t.start()
    sleep(1) # simplest way to give the dev server time to start

def test_default_response():
    assert requests.get(service_url).text.startswith('Hello,')

def test_can_change_response():
    res = requests.post(change_url, json=dict(code=500, body='problems'))
    assert res.json() == 'ok'
    res = requests.post(change_url, json=dict(code=200, body='Hello, w'))
    assert res.json() == 'ok'

def test_failed_change_response():
    res = requests.post(change_url, json=dict(foo=0))
    assert res.status_code == 400

def test_changing_affects_service():
    res = requests.post(change_url, json=dict(code=500, body='illuminati!'))
    assert res.json() == 'ok'
    assert requests.get(service_url).status_code == 500
    res = requests.post(change_url, json=dict(code=200, body='Hello, no prob!'))
    assert res.json() == 'ok'
    res = requests.get(service_url)
    assert res.status_code == 200
    assert res.text.startswith('Hello, no prob')

