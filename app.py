
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ C3P 雲端 Python Runner 正常運作中"

@app.route("/run", methods=["GET"])
def run_code():
    code = request.args.get("code", "")
    try:
        exec_locals = {}
        decoded = base64.b64decode(code).decode("utf-8")
        exec(decoded, {}, exec_locals)
        return jsonify(result=exec_locals.get("result", "No result"))
    except Exception as e:
        return jsonify(error=str(e))
