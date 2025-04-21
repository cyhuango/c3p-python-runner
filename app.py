@app.route('/run', methods=['POST'])
def run_code():
    global last_status, log_list
    try:
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
            "print": print
        }

        # 捕捉 print 輸出
        from io import StringIO
        import sys
        stdout_capture = StringIO()
        sys_stdout_backup = sys.stdout
        sys.stdout = stdout_capture

        # 執行程式碼
        exec(code, safe_env, safe_env)

        # 恢復 stdout
        sys.stdout = sys_stdout_backup
        printed_output = stdout_capture.getvalue().strip()

        # 優先取 result，否則取 print 輸出
        result = safe_env.get('result', None)
        if result is None and printed_output:
            result = printed_output
        elif not isinstance(result, (str, int, float, list, dict)):
            result = str(result)  # ⛑ 防崩潰轉換
        
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
