from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Allows requests from frontend

# Simple in-memory state (not persistent)
state = {
    "shivam": {"isOn": False, "totalTime": 0, "lastUpdate": time.time()},
    "devansh": {"isOn": False, "totalTime": 0, "lastUpdate": time.time()}
}

@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(state)

@app.route("/state", methods=["POST"])
def update_state():
    data = request.get_json()
    if "shivam" in data and "devansh" in data:
        state["shivam"].update(data["shivam"])
        state["devansh"].update(data["devansh"])
        return jsonify({"message": "State updated"}), 200
    return jsonify({"error": "Invalid state format"}), 400

if __name__ == "__main__":
    app.run(debug=True)
