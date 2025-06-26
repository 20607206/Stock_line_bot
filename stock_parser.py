import datetime
import json
import twstock
import yfinance
import pandas as pd
import re

with open("stock_bidirectional_map.json", "r", encoding="utf-8") as stock:
    maps = json.load(stock)

#  辨識文字內容
def resolve_stock_code(user_input):
    tw_name_to_code = maps['tw']['name_to_code']
    tw_code_to_code = maps['tw']['code_to_code']
    us_name_to_code = maps['us']['name_to_code']
    us_code_to_code = maps['us']['code_to_code']

    user_input = user_input.upper()

    if user_input in tw_code_to_code:
        return user_input
    if user_input in us_code_to_code:
        return user_input

    for tw_name in tw_name_to_code:
        if tw_name in user_input:
            code = tw_name_to_code.get(tw_name)
            return code
    for us_name in us_name_to_code:
        if us_name in user_input:
            code = us_name_to_code.get(us_name)
            return code

    possible_codes = re.findall(r'\d{4,6}|[A-Z]+', user_input)
    for code in possible_codes:
        if code in tw_code_to_code or us_code_to_code or code:
            return code
    print(f"🧪 resolved code: {code}, is_tw: {is_tw_stock(code)}")
    return f"{user_input}"

#  設定使用者搜尋天數(預設回傳1d)
def parse_period(user_input):
    period_mapping = maps["period_mapping"]
    for day in period_mapping:
        if day in user_input:
            period = period_mapping.get(day)
            return period
    return "1d"

#  處理股票編號對應名稱
def get_stock_name(stock_code):
    tw_code_to_name = maps['tw']['code_to_name']
    us_code_to_name = maps['us']['code_to_name']

    stock_code = stock_code.upper()

    if stock_code.isdigit():
        return tw_code_to_name.get(stock_code, "未知公司")
    else:
        return us_code_to_name.get(stock_code, "未知公司")

# 判斷是否為台股
def is_tw_stock(stock_code):
    return stock_code.isdigit()

# 主資料源：twstock（台股即時）
def get_twstock_price(stock_code):
    try:
        realtime_data = twstock.realtime.get(stock_code)

        if realtime_data and realtime_data["realtime"]:
            info = realtime_data.get("info", {})
            rt = realtime_data.get("realtime", {})
            df = pd.DataFrame([{
                "code": info.get("code"),
                "name": info.get("name"),
                "period": "1d",
                "date": info.get("time"),
                "Open": float(rt.get("open")),
                "Close": float(rt.get("latest_trade_price")),
                "High": float(rt.get("high")),
                "Low": float(rt.get("low")),
                "source": "資料來源:twstock(主資料)"
            }])
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df.set_index("date", inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"{e}")
        return pd.DataFrame()

# yfinance：台股或美股多日查詢
def get_yfinance_price(stock_code, period, is_tw = True):
    try:
        code = f"{stock_code}.TW" if is_tw else stock_code
        ticker = yfinance.Ticker(code)
        df = ticker.history(period= period)
        df["code"] = stock_code
        df["name"] = get_stock_name(stock_code)
        df["source"] = f"資料來源:yfinance({'台股備援' if is_tw else '美股'})"
        df["period"] = period
        return df
    except Exception as e:
        print(f"{e}")
        return pd.DataFrame()

#  查詢函式
def get_stock_data(stock_code, period):
    if is_tw_stock(stock_code):
        if period == "1d":
            df = get_twstock_price(stock_code)
            if df.empty:
                df = get_yfinance_price(stock_code, period, is_tw=True)
        else:
            df = get_yfinance_price(stock_code, period, is_tw=True)
    else:
        df = get_yfinance_price(stock_code, period, is_tw=False)
    return df

#  包裝對接Line bot
def line_text(user_input):
    from sql import load_stock_from_mysql
    try:
        stock_code = resolve_stock_code(user_input)
        period = parse_period(user_input)
        respond = load_stock_from_mysql(stock_code, period)
        result_text = format_stock_text(respond)
        return result_text
    except Exception as e:
        return f"請檢查股票代碼是否正確{e}"

#  安全轉換
def safe_float(value):
    try:
        return f"{float(value):.2f}"
    except:
        return "--"

#  輸出為文字
def format_stock_text(df):
    if df.empty:
        return "無法取得資料，請確認股票代碼與期間"

    stock_code = df["code"].iloc[0]
    name = df["name"].iloc[0]
    source = df["source"].iloc[0]
    period = df["period"].iloc[0]
    tw_time = datetime.timezone(datetime.timedelta(hours=8))
    time = datetime.datetime.now()
    query_time = time.now(tz=tw_time).strftime("%H:%M:%S")
    result_text = [
        f"{'=' * 24}\n"
        f"股票代碼:{stock_code}\n"
        f"股票名稱:{name}\n"
        f"查詢區間:{period}\n"
        f"{'=' * 24}"
    ]
    for date, row in df.iterrows():
        data_date = date.strftime("%Y-%m-%d")


        data_line = (
            f"📅資料日期:{data_date}\n"
            f"📈開:{safe_float(row['Open'])}｜收:{safe_float(row['Close'])}\n"
            f"📊高:{safe_float(row['High'])}｜低:{safe_float(row['Low'])}\n"
            
            f"{'=' * 24}"
         )
        result_text.append(data_line)

    result_text.append(f"查詢時間:{query_time}")
    result_text.append(source)

    return "\n".join(result_text)
