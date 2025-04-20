from flask import Flask, request, jsonify, send_from_directory
import base64
import traceback
import time
import os

# 記憶體記錄區
last_status = {
    "code": None,
    "result": None,
    "error": None,
    "timestamp": None
}
log_list = []

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_code():
    global last_status, log_list
    try:
        data = request.get_json()
        code_b64 = data.get('code')
        if not code_b64:
            return jsonify({'error': 'Missing code parameter'}), 400

        code_bytes = base64.b64decode(code_b64)
        code = code_bytes.decode('utf-8')

        safe_env = {
            "__builtins__": __builtins__,
            "random": __import__('random'),
            "math": __import__('math'),
            "datetime": __import__('datetime'),
            "statistics": __import__('statistics'),
            "decimal": __import__('decimal')
        }

        exec(code, safe_env, safe_env)

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        result = safe_env.get('result') or {k: v for k, v in safe_env.items() if not k.startswith("__")}
        last_status = {"code": code, "result": result, "error": None, "timestamp": timestamp}
        log_list.append(last_status)
        if len(log_list) > 100:
            log_list.pop(0)

        return jsonify({'result': result})
    except Exception as e:
        err_info = {"error": str(e), "traceback": traceback.format_exc()}
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        last_status = {"code": code if 'code' in locals() else None, "result": None, "error": err_info, "timestamp": timestamp}
        log_list.append(last_status)
        if len(log_list) > 100:
            log_list.pop(0)
        return jsonify(err_info), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'message': 'Runner is awake.'})

@app.route('/status', methods=['GET'])
def status():
    return jsonify(last_status)

@app.route('/log', methods=['GET'])
def log():
    return jsonify({"log":
