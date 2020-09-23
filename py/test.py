from flask import Flask,jsonify,render_template
from flask_cors import CORS
import random
import json

app = Flask(__name__)
CORS(app, resources=r'/*')

@app.route('/get_data')
def get_data():
    data = {
        'data': []
    }
    for _ in range(300):
        data['data'].append([random.random(), random.random(), random.random()])
    for _ in range(900):
        data['data'].append([5*random.random(), 5*random.random(), random.random()/2])
    return json.dumps(data)

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 7777,
        debug = True
    )