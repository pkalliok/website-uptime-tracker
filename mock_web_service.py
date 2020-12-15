from flask import Flask
mock = Flask(__name__)

http_code = None
content = "Hello, I'm a happy web service, nice to meet you!\n"

@mock.route('/service')
def mock_service():
    return content, http_code

