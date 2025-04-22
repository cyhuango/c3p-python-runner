from flask import Flask, request, jsonify, send_file
import base64, traceback, time, os, json
from io import StringIO
import sys
import uuid

# ✅ 模組預檢區（sympy 是否可用）
try:
    from sympy import symbols, Eq, solve
    sympy_available = True
except ImportError:
    sympy_available = False

app = Flask(__name__)

__version__ = "1.2"
__build__ = "LEAD_ONE_PLUGIN_SUITE_v1.1.1"

# ✅ 格式化時間字串工具
def format_time(h, m, pad=True):
    if pad:
        return "{:02d}:{:02d}".format(h, m)
    else:
        return "{}:{}".format(h, m)

# ✅ JSON 安全輸出過濾（保證 serializable）
def make_json_safe(val):
    try:
        json.dumps(val)
        return val
    except TypeError:
        return str(val)

# 記憶狀態
last_status = {"code": None, "result": None, "error": None, "timestamp": None}
log_list = []

@app.route('/run', methods=['POST'])
def run_code():
    global last_status, log_list
    trace_id = str(uuid.uuid4())
    auto_patch_applied = request.json.get("auto_patch_applied", False)

    try:
        # ⛑ 解碼前防錯
        try:
            code_b64 = request.get_json().get('code')
            code = base64.b64decode(code_b64).decode('utf-8')
        except Exception as decode_err:
            return jsonify({
                "error": "Invalid base64 or UTF-8 decoding",
                "trace_id": trace_id,
                "module_missing": None,
                "auto_patch_applied": False
            }), 400

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
            "format_time": format_time
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

        # 優先 result，其次印出
        result = safe_env.get('result', None)
        if result is None and printed_output:
            result = printed_output
        elif not isinstance(result, (str, int, float, list, dict)):
            result = make_json_safe(result)

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        last_status = {
            "code": code,
            "result": result,
            "error": None,
            "timestamp": timestamp
        }
        log_list.append(last_status)
        if len(log_list) > 100:
            log_list.pop(0)

        return jsonify({
            "result": result,
            "status": "success",
            "trace_id": trace_id,
            "module_missing": not sympy_available,
            "auto_patch_applied": auto_patch_applied
        })

    except Exception as e:
        err = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "trace_id": trace_id,
            "status": "error",
            "module_missing": "sympy" if "sympy" in str(e) else None,
            "auto_patch_applied": auto_patch_applied
        }
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        last_status = {
            "code": code if 'code' in locals() else None,
            "result": None,
            "error": err,
            "timestamp": timestamp
        }
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
    return jsonify({
        "status": "ok",
        "message": "Runner is awake.",
        "version": f"LEAD_ONE_RUNNER v{__version__}",
        "build": __build__,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sympy": sympy_available
    })

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
