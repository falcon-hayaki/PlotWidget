from flask import Flask,jsonify,render_template
from flask_cors import CORS
import random
import json

from HCAd_Client.HCAd_Client import HCAd_Client

app = Flask(__name__)
CORS(app, resources=r'/*')

@app.route('/api_get_data')
def get_data():
    data = {
        'data': []
    }

    req_data = json.loads(request.get_data(as_text=True))
    conditions = req_data['conditions']
    col = req_data['col']

    db = HCAd_Client()
    db.Setup_Client(endpoint, access_key_id, access_key_secret, instance_name, table_name)

    rows = db.query_cells(conditions)

    df = db.get_columnsbycell(rows, col)

    return data

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 7777,
        debug = True
    )