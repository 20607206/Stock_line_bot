import json
import twstock
import yfinance
import pandas as pd

with open("stock_bidirectional_map.json", "r", encoding="utf-8") as stock:
    maps = json.load(stock)

#  辨識文字內容
def resolve_stock_code(user_input):
    tw_name_to_code = maps['tw']['name_to_code']
    tw_code_to_code = maps['tw']['code_to_code']
    us_name_to_code = maps['us']['name_to_code']
    us_code_to_code = maps['us']['code_to_code']

    user_input = user_input.upper()
    for tw_name in tw_name_to_code:
        if tw_name in user_input:
            tw_code = tw_name_to_code.get(tw_name)
            return tw_code

    for us_name in us_name_to_code:
        if us_name in user_input:
            us_code = us_name_to_code.get(us_name)
            return us_code

    for code in us_code_to_code:
        if code in user_input:
            us_code = us_code_to_code.get(code)
            return us_code

    for code in tw_code_to_code:
        if code in user_input:
            tw_code = tw_code_to_code.get(code)
            return tw_code

    return user_input

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
        source = "資料來源:twstock(主資料)"
        period = "1d"
        if realtime_data and realtime_data["realtime"]:
            info = realtime_data.get("info", {})
            rt = realtime_data.get("realtime", {})
            df = pd.DataFrame([{
                "code": info.get("code"),
                "name": info.get("name"),
                "period": period,
                "date": info.get("time"),
                "Open": rt.get("open"),
                "Close": rt.get("latest_trade_price"),
                "High": rt.get("high"),
                "Low": rt.get("low"),
                "source": source
            }])
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df.set_index("date", inplace=True)
            return df
    except Exception as e:
        return f"{e}"

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
        pd.set_option('display.width', None)
        return df
    except Exception as e:
        return f"{e}"

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
    code = resolve_stock_code(user_input)
    period = parse_period(user_input)
    respond = get_stock_data(code, period)
    result_text = format_stock_text(respond)
    return result_text

# 輸出為文字
def format_stock_text(df):
    if df.empty:
        return "無法取得資料，請確認股票代碼與期間"

    stock_code = df["code"].iloc[0]
    name = df["name"].iloc[0]
    source = df["source"].iloc[0]
    period = df["period"].iloc[0]

    result_text = [
        f"{'=' * 24}\n"
        f"股票代碼:{stock_code}\n"
        f"股票名稱:{name}\n"
        f"查詢區間:{period}\n"
        f"{'=' * 24}\n"
    ]
    for date, row in df.iterrows():
        date = date.strftime("%Y-%m-%d  %H-%M")
        data_line = (
            f"📅{date}\n"
            f"📈開:{float(row['Open']):.2f}｜收:{float(row['Close']):.2f}\n"
            f"📊高:{float(row['High']):.2f}｜低:{float(row['Low']):.2f}\n"
            f"{'=' * 24}\n"
         )
        result_text.append(data_line)

    result_text.append(source)

    return "\n".join(result_text)

df = line_text("00881")
print(df)
