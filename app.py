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

        # 建立一個局部變數空間
        local_vars = {}
        exec(code, {}, local_vars)

        # 回傳 result，如果有的話
        if 'result' in local_vars:
            return jsonify({'result': local_vars['result']})
        else:
            return jsonify({'output': local_vars})
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/', methods=['GET'])
def home():
    return "🟢 Python Runner API Online. Use POST /run with base64 Python code."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
