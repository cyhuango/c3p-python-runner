from flask import Flask, request, jsonify
import base64
import traceback

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_code():
    try:
        data = request.get_json()
        code_b64 = data.get('code')
        if not code_b64:
            return jsonify({'error': 'Missing code parameter'}), 400

        code_bytes = base64.b64decode(code_b64)
        code = code_bytes.decode('utf-8')

        # ✅ 修正：統一執行環境，支援模組與變數共用
        safe_env = {
            "__builtins__": __builtins__,
            "random": __import__('random')
        }

        exec(code, safe_env, safe_env)

        # 嘗試取出 result 變數
        if 'result' in safe_env:
            return jsonify({'result': safe_env['result']})
        else:
            return jsonify({'output': {k: v for k, v in safe_env.items() if not k.startswith('__')}})
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'message': 'Runner is awake.'})

@app.route('/', methods=['GET'])
def home():
    return "🟢 Python Runner API Online. Use POST /run with base64 Python code."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
