from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import time
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

STATUS_FILE = 'status.json'
LOG_FILE = 'log.json'
RESUME_THRESHOLD = 5 * 60  # 5 minutes in seconds

def now_ts():
    return int(time.time())

def get_status():
    if not os.path.exists(STATUS_FILE):
        return {'ac': 'none', 'startTime': None, 'lastOffTime': None}
    with open(STATUS_FILE, 'r') as f:
        return json.load(f)

def set_status(data):
    with open(STATUS_FILE, 'w') as f:
        json.dump(data, f)

def append_log(room, start_time, end_time):
    duration = end_time - start_time
    log_entry = {
        "room": room,
        "date": datetime.utcfromtimestamp(end_time).strftime('%Y-%m-%d'),
        "start": start_time,
        "end": end_time,
        "duration": duration
    }
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    logs.append(log_entry)
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/status', methods=['GET'])
def status():
    data = get_status()
    return jsonify({
        'ac': data['ac'],
        'startTime': data['startTime']
    })

@app.route('/api/set', methods=['POST'])
def set_ac():
    data = request.json
    status_data = get_status()
    now = now_ts()

    if status_data['ac'] != 'none' and status_data['ac'] != data['room']:
        return jsonify({'status': 'conflict', 'ac': status_data['ac']}), 409

    resume = False
    if status_data['lastOffTime']:
        if now - status_data['lastOffTime'] < RESUME_THRESHOLD:
            resume = True

    new_start_time = status_data['startTime'] if resume and status_data['startTime'] else now

    new_status = {
        'ac': data['room'],
        'startTime': new_start_time,
        'lastOffTime': None
    }

    set_status(new_status)
    return jsonify({'status': 'ok', 'ac': data['room'], 'startTime': new_start_time})

@app.route('/api/off', methods=['POST'])
def turn_off():
    status_data = get_status()
    now = now_ts()

    if status_data['ac'] != 'none' and status_data['startTime']:
        append_log(status_data['ac'], status_data['startTime'], now)

    set_status({
        'ac': 'none',
        'startTime': None,
        'lastOffTime': now
    })
    return jsonify({'status': 'ok', 'ac': 'none'})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify([])
    with open(LOG_FILE, 'r') as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'w') as f:
            json.dump({'ac': 'none', 'startTime': None, 'lastOffTime': None}, f)
    app.run(host='0.0.0.0', port=5000)
