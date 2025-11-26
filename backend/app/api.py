# backend/app/api.py
# Simple dev server for the DevOps Playground with Socket.IO + CORS
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import uuid, time, threading

# Create app and enable CORS for /api/*
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Create Socket.IO server; allow all origins for local dev
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory "database" for demo pipeline runs
PIPELINE_DB = {}

# Simple health endpoint
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# List past pipeline runs
@app.route("/api/pipelines", methods=["GET"])
def list_pipelines():
    return jsonify(list(PIPELINE_DB.values())), 200

# Start a pipeline run (simulated). Returns an id immediately (202).
@app.route("/api/pipelines/run", methods=["POST"])
def run_pipeline():
    payload = request.get_json() or {}
    print("DEBUG: Received pipeline run request, payload:", payload)
    pid = str(uuid.uuid4())
    PIPELINE_DB[pid] = {"id": pid, "status": "running", "stages": []}
    # Start the simulated pipeline in a background thread
    thread = threading.Thread(target=simulate_run, args=(pid,))
    thread.daemon = True
    thread.start()
    print("DEBUG: Started pipeline", pid)
    return jsonify({"id": pid}), 202

# Simulate pipeline stages and emit logs over Socket.IO
def simulate_run(pid):
    stages = ["checkout", "build", "test", "scan", "push", "deploy"]
    for s in stages:
        start_msg = f"Starting {s}"
        PIPELINE_DB[pid]["stages"].append({"name": s, "status": "running"})
        socketio.emit("log", {"pid": pid, "stage": s, "msg": start_msg})
        print(f"DEBUG EMIT: pid={pid} stage={s} msg={start_msg}")
        time.sleep(1)  # simulate work
        PIPELINE_DB[pid]["stages"][-1]["status"] = "done"
        end_msg = f"Finished {s}"
        socketio.emit("log", {"pid": pid, "stage": s, "msg": end_msg})
        print(f"DEBUG EMIT: pid={pid} stage={s} msg={end_msg}")

    PIPELINE_DB[pid]["status"] = "success"
    socketio.emit("pipeline_done", {"pid": pid})
    print(f"DEBUG: pipeline {pid} done, emitted pipeline_done")

# Manual test endpoint to emit a single log (useful to verify sockets)
@app.route("/api/emit_test", methods=["GET"])
def emit_test():
    socketio.emit("log", {"pid": "manual", "stage": "manual", "msg": "Manual emit test"})
    print("DEBUG: manual emit sent")
    return jsonify({"ok": True}), 200

# Optional: print when a client connects (server-side)
@socketio.on("connect")
def handle_connect():
    try:
        sid = request.sid
    except Exception:
        sid = "<unknown>"
    print("DEBUG: Socket connected, sid=", sid)

# Run the app. For local dev we prefer an async worker (eventlet) if installed.
if __name__ == "__main__":
    try:
        import eventlet  # noqa: F401
        # If eventlet is available, socketio.run() will use it.
        socketio.run(app, host="0.0.0.0", port=5000)
    except Exception:
        # fallback for quick development: allow Werkzeug explicitly
        socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
