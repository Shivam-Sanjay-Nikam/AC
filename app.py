from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json, os, time
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

STATUS_FILE = 'status.json'
FIVE_MIN = 5 * 60

def now(): return int(time.time())

def get_status():
    if not os.path.exists(STATUS_FILE):
        return {"ac": "none", "startTime": None, "duration": 0, "lastAC": None, "lastOffTime": None}

    with open(STATUS_FILE, 'r') as f:
        return json.load(f)

def save_status(data):
    with open(STATUS_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/status', methods=['GET'])
def status():
    data = get_status()
    if data['ac'] != 'none' and data['startTime']:
        duration = now() - data['startTime'] + data.get('duration', 0)
    else:
        duration = data.get('duration', 0)
    data['displayDuration'] = duration
    return jsonify(data)

@app.route('/api/set', methods=['POST'])
def turn_on():
    data = get_status()
    req = request.get_json()
    room = req.get('room')
    current_time = now()

    if data['ac'] != 'none':
        return jsonify({'status': 'conflict', 'ac': data['ac']}), 409

    # Check if resumed within 5 mins
    if data.get('lastAC') == room and data.get('lastOffTime') and current_time - data['lastOffTime'] < FIVE_MIN:
        # resume timer
        data['ac'] = room
        data['startTime'] = current_time
    else:
        data = {
            "ac": room,
            "startTime": current_time,
            "duration": 0,
            "lastAC": room,
            "lastOffTime": None
        }

    save_status(data)
    return jsonify({'status': 'ok', 'ac': room})

@app.route('/api/off', methods=['POST'])
def turn_off():
    data = get_status()
    if data['ac'] != 'none' and data.get('startTime'):
        elapsed = now() - data['startTime']
        data['duration'] = data.get('duration', 0) + elapsed
        data['lastAC'] = data['ac']
        data['lastOffTime'] = now()

    data['ac'] = 'none'
    data['startTime'] = None
    save_status(data)
    return jsonify({'status': 'ok', 'ac': 'none'})

if __name__ == '__main__':
    if not os.path.exists(STATUS_FILE):
        save_status({"ac": "none", "startTime": None, "duration": 0, "lastAC": None, "lastOffTime": None})
    app.run(host='0.0.0.0', port=5000)
