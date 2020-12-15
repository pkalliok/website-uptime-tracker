from flask import Flask, jsonify, request
mock = Flask(__name__)

http_code = None
content = "Hello, I'm a happy web service, nice to meet you!\n"

@mock.route('/service')
def mock_service():
    return content, http_code

@mock.route('/changeResponse', methods=['POST'])
def change_service_response():
    params = request.json
    try: http_code = params['code']
    except KeyError: return jsonify('"code" parameter missing'), 400
    if 'body' in params: content = params['body']
    return jsonify('ok')

