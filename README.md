# C3P Python Runner

這是雲端任務執行器，用於接收 base64 編碼的 Python 程式碼，並在 Render 上執行後回傳結果。

## 使用方式

傳送 GET 請求至 `/run?code=xxx`  
其中 `xxx` 為 base64 編碼的 Python 程式（需包含 `result = ...`）

---

## 🔧 執行規則（依 runner-rules.json）

- 接收格式：Base64 UTF-8 編碼字串（Python 程式）
- 回傳類型：JSON 可序列化類別（str/int/list/dict）
- 捕捉 print() → stdout
- 自動降級非序列型為 `str()`
- 錯誤包裝為 `{ error, traceback }`

---

## 📎 執行路徑

```bash
POST /run
GET  /status
GET  /log


部署於 Render，啟動方式使用 gunicorn。
