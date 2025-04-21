from flask import Flask, request, jsonify, send_file
import base64, traceback, time, os, json
from io import StringIO
import sys

app = Flask(__name__)

# 記憶狀態
last_status = {"code": None, "result": None, "error": None, "timestamp": None}
log_list = []

@app.route('/run', methods=['POST'])
def run_code():
    global last_status, log_list
    try:
        # 解碼 base64 code
        code_b64 = request.get_json().get('code')
        code = base64.b64decode(code_b64).decode('utf-8')

        # 安全執行環境
        safe_env = {
            "__builtins__": __builtins__,
            "random": __import__('random'),
            "math": __import__('math'),
            "datetime": __import__('datetime'),
            "statistics": __import__('statistics'),
            "decimal": __import__('decimal'),
            "time": __import__('time'),
            "json": __import__('json'),
        }

        # 捕捉 print 輸出
        stdout_capture = StringIO()
        sys_stdout_backup = sys.stdout
        sys.stdout = stdout_capture

        # 執行程式
        exec(code, safe_env, safe_env)

        # 恢復 stdout
        sys.stdout = sys_stdout_backup
        printed_output = stdout_capture.getvalue().strip()

        # 取 result 或 print 輸出
        result = safe_env.get('result', None)
        if result is None and printed_output:
            result = printed_output
        elif not isinstance(result, (str, int, float, list, dict)):
            result = str(result)

        # 狀態記錄
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        last_status = {"code": code, "result": result, "error": None, "timestamp": timestamp}
        log_list.append(last_status)
        if len(log_list) > 100:
            log_list.pop(0)

        return jsonify({'result': result})

    except Exception as e:
        err = {"error": str(e), "traceback": traceback.format_exc()}
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        last_status = {"code": code if 'code' in locals() else None, "result": None, "error": err, "timestamp": timestamp}
        log_list.append(last_status)
        if len(log_list) > 100:
            log_list.pop(0)
        return jsonify(err), 500

@app.route('/status')
def status():
    return jsonify(last_status)

@app.route('/log')
def log():
    return jsonify({"log": log_list})

@app.route('/ping')
def ping():
    return jsonify({"status": "ok", "message": "Runner is awake."})

@app.route('/.well-known/ai-plugin.json')
def serve_ai_plugin():
    return send_file('ai-plugin.json', mimetype='application/json')

@app.route('/openapi.yaml')
def serve_openapi_yaml():
    return send_file('openapi.yaml', mimetype='text/yaml')

@app.route('/openapi.json')
def serve_openapi_json():
    with open('openapi.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/legal.html')
def serve_legal():
    return send_file('legal.html', mimetype='text/html')

@app.route('/logo.png')
def serve_logo():
    return send_file('logo.png', mimetype='image/png')

@app.route('/')
def home():
    return "🟢 Python Runner API Online. Use POST /run with base64 Python code."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
