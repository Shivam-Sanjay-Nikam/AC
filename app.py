from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json, os, time
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

STATUS_FILE = 'status.json'
LOG_FILE = 'log.json'
COOLDOWN_SECONDS = 300  # 5 minutes

def get_status():
    with open(STATUS_FILE, 'r') as f:
        return json.load(f)

def set_status(data):
    with open(STATUS_FILE, 'w') as f:
        json.dump(data, f)

def log_session(room, start, end):
    entry = {
        "room": room,
        "start": datetime.utcfromtimestamp(start).isoformat(),
        "end": datetime.utcfromtimestamp(end).isoformat(),
        "duration_seconds": int(end - start)
    }
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump([entry], f, indent=2)
    else:
        with open(LOG_FILE, 'r+') as f:
            log = json.load(f)
            log.append(entry)
            f.seek(0)
            json.dump(log, f, indent=2)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/status')
def status():
    status = get_status()
    return jsonify(status)

@app.route('/api/set', methods=['POST'])
def turn_on():
    data = request.get_json()
    room = data['room']
    now = int(time.time())
    status = get_status()

    if status['ac'] == room:
        return jsonify({'ac': room, 'startTime': status['startTime']})

    if status['ac'] != 'none':
        return jsonify({'status': 'conflict', 'ac': status['ac']}), 409

    last_off = status.get('lastOffTime', 0)
    last_room = status.get('lastRoom', None)
    reuse_start = (now - last_off <= COOLDOWN_SECONDS and last_room == room)

    start_time = status.get('startTime') if reuse_start else now

    set_status({
        'ac': room,
        'startTime': start_time,
        'lastRoom': room
    })

    return jsonify({'ac': room, 'startTime': start_time})

@app.route('/api/off', methods=['POST'])
def turn_off():
    now = int(time.time())
    status = get_status()
    if status['ac'] != 'none':
        log_session(status['ac'], status['startTime'], now)

    set_status({
        'ac': 'none',
        'lastRoom': status.get('ac'),
        'lastOffTime': now
    })

    return jsonify({'status': 'ok', 'ac': 'none'})

if __name__ == '__main__':
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'w') as f:
            json.dump({'ac': 'none'}, f)
    app.run(host='0.0.0.0', port=5000)
