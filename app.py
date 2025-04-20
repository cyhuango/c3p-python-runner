from flask import Flask, request, jsonify, send_file
import base64, traceback, time, os

app = Flask(__name__)

# 執行狀態記憶
last_status = {"code": None, "result": None, "error": None, "timestamp": None}
log_list = []

@app.route('/run', methods=['POST'])
def run_code():
    global last_status, log_list
    try:
        code_b64 = request.get_json().get('code')
        code = base64.b64decode(code_b64).decode('utf-8')
        safe_env = {
            "__builtins__": __builtins__,
            "random": __import__('random'),
            "math": __import__('math'),
            "datetime": __import__('datetime'),
            "statistics": __import__('statistics'),
            "decimal": __import__('decimal')
        }
        exec(code, safe_env, safe_env)
        result = safe_env.get('result') or {k: v for k, v in safe_env.items() if not k.startswith('__')}
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        last_status = {"code": code, "result": result, "error": None, "timestamp": timestamp}
        log_list.append(last_status)
        if len(log_list) > 100: log_list.pop(0)
        return jsonify({'result': result})
    except Exception as e:
        err = {"error": str(e), "traceback": traceback.format_exc()}
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        last_status = {"code": code if 'code' in locals() else None, "result": None, "error": err, "timestamp": timestamp}
        log_list.append(last_status)
        if len(log_list) > 100: log_list.pop(0)
        return jsonify(err), 500

@app.route('/status')
def status(): return jsonify(last_status)

@app.route('/log')
def log(): return jsonify({"log": log_list})

@app.route('/ping')
def ping(): return jsonify({"status": "ok", "message": "Runner is awake."})

# ✅ Plugin: .well-known/ai-plugin.json
@app.route('/.well-known/ai-plugin.json')
def serve_ai_plugin():
    return jsonify({
        "schema_version": "v1",
        "name_for_human": "LEAD ONE Python Runner",
        "name_for_model": "lead_one_py_runner",
        "description_for_human": "Execute secure Python code via API.",
        "description_for_model": "Run base64 encoded Python code and retrieve results through the /run endpoint.",
        "auth": { "type": "none" },
        "api": {
            "type": "openapi",
            "url": "https://c3p-python-runner.onrender.com/openapi.json"
        },
        "logo_url": "https://c3p-python-runner.onrender.com/logo.png",
        "contact_email": "cyhuango@gmail.com",
        "legal_info_url": "https://c3p-python-runner.onrender.com/legal.html"
    })

# ✅ Plugin: openapi.yaml
@app.route('/openapi.yaml')
def serve_openapi():
    with open('openapi.yaml', 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/yaml'}

# ✅ Plugin: openapi.json
@app.route('/openapi.json')
def serve_openapi_json():
    return send_file('openapi.json', mimetype='application/json')

# ✅ Plugin: legal.html
@app.route('/legal.html')
def serve_legal():
    return send_file('legal.html', mimetype='text/html')

@app.route('/')
def home(): return "🟢 Python Runner API Online. Use POST /run with base64 Python code."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
