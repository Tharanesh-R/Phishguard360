"""
CyberShield Native Messaging Host
==================================
This script is launched by Chrome via Native Messaging to auto-start
the Flask backend server. It follows the Chrome Native Messaging protocol
(length-prefixed JSON on stdin/stdout).

Flow:
1. Chrome extension sends {"action": "start_server"}
2. This host checks if the server is already running
3. If not, starts app.py as a detached background process
4. Sends back {"status": "running", "port": 5000}
"""

import sys
import os
import json
import struct
import subprocess
import time
import socket

# Resolve paths relative to this script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)  # Parent directory
APP_PY = os.path.join(PROJECT_DIR, "app.py")
PYTHON_EXE = sys.executable
BACKEND_PORT = 5000
BACKEND_HOST = "127.0.0.1"


def is_server_running():
    """Check if the Flask backend is already running on the expected port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((BACKEND_HOST, BACKEND_PORT))
        sock.close()
        return result == 0
    except Exception:
        return False


def start_server():
    """Start app.py as a detached background process."""
    if not os.path.exists(APP_PY):
        return {"status": "error", "message": f"app.py not found at {APP_PY}"}

    try:
        # Use DETACHED_PROCESS flag on Windows so the server keeps running
        # even after this native host process exits
        CREATE_NO_WINDOW = 0x08000000
        DETACHED_PROCESS = 0x00000008

        process = subprocess.Popen(
            [PYTHON_EXE, APP_PY],
            cwd=PROJECT_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
            close_fds=True
        )

        # Wait for server to become available (max 10 seconds)
        for i in range(20):
            time.sleep(0.5)
            if is_server_running():
                return {
                    "status": "started",
                    "pid": process.pid,
                    "port": BACKEND_PORT,
                    "message": "CyberShield backend started successfully"
                }

        return {
            "status": "timeout",
            "pid": process.pid,
            "message": "Server process started but port not yet available"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# =============================
# Native Messaging Protocol
# =============================

def read_message():
    """Read a native messaging message from stdin."""
    # Read 4-byte message length
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length or len(raw_length) < 4:
        return None
    length = struct.unpack('I', raw_length)[0]
    # Read the message
    raw_message = sys.stdin.buffer.read(length)
    if not raw_message:
        return None
    return json.loads(raw_message.decode('utf-8'))


def send_message(message):
    """Send a native messaging message to stdout."""
    encoded = json.dumps(message).encode('utf-8')
    length = struct.pack('I', len(encoded))
    sys.stdout.buffer.write(length)
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


def main():
    """Main loop: read one message, process it, respond, then exit."""
    try:
        message = read_message()

        if not message:
            send_message({"status": "error", "message": "No message received"})
            return

        action = message.get("action", "")

        if action == "start_server":
            if is_server_running():
                send_message({
                    "status": "already_running",
                    "port": BACKEND_PORT,
                    "message": "Backend is already running"
                })
            else:
                result = start_server()
                send_message(result)

        elif action == "check_status":
            running = is_server_running()
            send_message({
                "status": "running" if running else "stopped",
                "port": BACKEND_PORT
            })

        elif action == "ping":
            send_message({"status": "pong", "host": "cybershield_host"})

        else:
            send_message({"status": "error", "message": f"Unknown action: {action}"})

    except Exception as e:
        try:
            send_message({"status": "error", "message": str(e)})
        except Exception:
            pass


if __name__ == "__main__":
    main()
