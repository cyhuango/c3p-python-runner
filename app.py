# app.py（LEAD ONE Runner 核心邏輯）
# __version__ 與 __build__ 為同步三件套與回傳規則的重要標籤

from flask import Flask, request, jsonify
import base64
import traceback
import uuid

# 模組偵測區
try:
    from sympy import symbols, Eq, solve
    sympy_available = True
except ImportError:
    sympy_available = False

app = Flask(__name__)

__version__ = "1.2"
__build__ = "LEAD_ONE_PLUGIN_SUITE_v1.1.1"

@app.route("/run", methods=["POST"])
def run_code():
    code = base64.b64decode(request.json["code"]).decode("utf-8")
    exec_globals = {"__builtins__": __builtins__}
    result = None
    trace_id = str(uuid.uuid4())
    auto_patch_applied = request.json.get("auto_patch_applied", False)

    try:
        exec(code, exec_globals)
        result = exec_globals.get("result", None)
        return jsonify({
            "result": result,
            "status": "success",
            "trace_id": trace_id,
            "module_missing": not sympy_available,
            "auto_patch_applied": auto_patch_applied
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": e.__class__.__name__,
            "trace_id": trace_id,
            "status": "error",
            "module_missing": "sympy" if "sympy" in str(e) else None,
            "auto_patch_applied": auto_patch_applied
        })

@app.route("/status")
def status():
    return {
        "version": __version__,
        "build": __build__,
        "sympy_installed": sympy_available,
        "runner": "LEAD ONE Python Plugin Runner"
    }
