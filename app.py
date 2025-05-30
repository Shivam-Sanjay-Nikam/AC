from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='static')
CORS(app)

STATUS_FILE = 'status.json'

def get_status():
    with open(STATUS_FILE, 'r') as f:
        return json.load(f)

def set_status(new_status):
    with open(STATUS_FILE, 'w') as f:
        json.dump(new_status, f)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(get_status())

@app.route('/api/set', methods=['POST'])
def set_ac():
    data = request.json
    current = get_status()
    if current['ac'] == 'none':
        set_status({'ac': data['room']})
        return jsonify({'status': 'ok', 'ac': data['room']})
    else:
        return jsonify({'status': 'conflict', 'ac': current['ac']}), 409

@app.route('/api/off', methods=['POST'])
def turn_off():
    set_status({'ac': 'none'})
    return jsonify({'status': 'ok', 'ac': 'none'})

if __name__ == '__main__':
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'w') as f:
            json.dump({'ac': 'none'}, f)
    app.run(host='0.0.0.0', port=5000)
