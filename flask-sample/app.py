import json

from flask import Flask

from werkzeug.wrappers import Response

app = Flask(__name__)


@app.route('/')
def index():
    return Response(response=json.dumps({'Hello': 'World'}), content_type='application/json')


if __name__ == '__main__':
    app.run()
