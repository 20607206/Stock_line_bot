# 股票查詢 Line Bot

這是一個用 Python 寫的 Line Bot，讓你可以用 Line 查股票，還會幫你把資料存在 MySQL，還會定時更新股票價格，資料來源有台股即時資料 (twstock) 跟 yfinance（備援台股＆美股）。

---

## 功能特色

- 輸入股票名稱或代碼，快速回傳股票資訊（開盤、收盤、最高、最低價）
- 支援台股和美股查詢
- 自動訂閱用戶查過的股票，定時幫你更新資料
- 資料存在 MySQL，節省爬取時間
- 使用 Heroku Schedule，每天下午 2:30 (台灣時間) 自動更新收盤後資料
- 回覆時間顯示為台灣時區時間

---

## 環境需求

- Python 3.8+
- MySQL 資料庫
- Line Messaging API 帳號（需取得 Channel Access Token 與 Channel Secret）
- Heroku（用來部署及排程）
- 以下 Python 套件：
  - flask
  - line-bot-sdk
  - pandas
  - mysql-connector-python
  - python-dotenv
  - twstock
  - yfinance

---

## 環境變數設定

請在 `.env` 檔案或 Heroku Config Vars 設定以下環境變數：

```env
LINE_CHANNEL_ACCESS_TOKEN=你的Line Channel Access Token
LINE_CHANNEL_SECRET=你的Line Channel Secret

MYSQL_HOST=你的MySQL主機
MYSQL_PORT=你的MySQL連接埠
MYSQL_USER=你的MySQL帳號
MYSQL_PASSWORD=你的MySQL密碼
MYSQL_DATABASE=你的MySQL資料庫名稱
```
## 使用說明

1:將專案 clone 下來
2:安裝相依套件：
    pip install -r requirements.txt
3:配置好 .env 或 Heroku Config Vars 並部署到 Heroku
4:透過 Line 聊天視窗輸入股票代碼或名稱，即可查詢股票資訊

## 定時更新

- 專案使用 Heroku Scheduler 設定排程：
- 執行指令：python stock_job.py
- 頻率設定：每天 14:30 (台灣時間) 收盤後自動更新資料

## 注意事項

- 目前系統僅支援「盤後查詢」📉，每日約於台灣時間 14:30 後 自動更新資料。
- 若於盤中查詢，資料將為前一個交易日的收盤資訊。
- 若查不到即時資料，系統會自動使用 yfinance 備援資料來源
- 回傳資料時間均為台灣時區時間，方便你看時間點
- 股票代碼辨識會自動識別股票名稱或代碼，還能解析輸入的查詢區間（例如「5d」）