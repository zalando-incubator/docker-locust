import json

from flask import Flask, request

from werkzeug.wrappers import Response

app = Flask(__name__)


@app.route('/', methods=['POST'])
def post_entry():
    params = request.get_json()
    return Response(response=json.dumps({'name': params.get('name'), 'gender': params.get('gender')}),
                    content_type='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
