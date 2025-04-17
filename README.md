# C3P Python Runner

這是雲端任務執行器，用於接收 base64 編碼的 Python 程式碼，並在 Render 上執行後回傳結果。

## 使用方式

傳送 GET 請求至 `/run?code=xxx`  
其中 `xxx` 為 base64 編碼的 Python 程式（需包含 `result = ...`）

回傳格式：
```json
{ "result": 你程式中定義的 result 變數內容 }
```

部署於 Render，啟動方式使用 gunicorn。
