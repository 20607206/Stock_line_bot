import json
import pandas as pd
import yfinance
import twstock

with open('stock_bidirectional_map.json', "r", encoding="utf-8") as name:
    maps = json.load(name)

#  辨識文字內容
def resolve_stock_code(text):
    tw_name_to_code = maps['tw']['name_to_code']
    tw_code_to_code = maps['tw']['code_to_code']
    us_name_to_code = maps['us']['name_to_code']
    us_code_to_code = maps['us']['code_to_code']

    text = text.upper()
    for tw_name in tw_name_to_code:
        if tw_name in text:
            tw_code = tw_name_to_code.get(tw_name)
            return tw_code

    for us_name in us_name_to_code:
        if us_name in text:
            us_code = us_name_to_code.get(us_name)
            return us_code

    for code in us_code_to_code:
        if code in text:
            us_code = us_code_to_code.get(code)
            return us_code

    for code in tw_code_to_code:
        if code in text:
            tw_code = tw_code_to_code.get(code)
            return tw_code

    return text

#  處理股票編號對應名稱
def get_stock_name(stock_code):
    tw_code_to_name = maps['tw']['code_to_name']
    us_code_to_name = maps['us']['code_to_name']

    if stock_code.isdigit():
        return tw_code_to_name.get(stock_code, "未知公司")
    else:
        return us_code_to_name.get(stock_code, "未知公司")

#  資料處理工具
def remove_trailing_zero(number_str):
    if '.' in number_str:
        number_str = number_str.rstrip('0').rstrip('.')
        return number_str

#  設定使用者搜尋天數(預設回傳1d)
def parse_period(user_input):
    period_mapping = maps["period_mapping"]
    for day in period_mapping:
        if day in user_input:
            period = period_mapping.get(day)
            return period
    return "1d"

def draw_stock_chart(df, period, stock_code, source):
    pass

#  處理文字輸出
def format_stock_text(df):
    stock_code = df["stock_code"].iloc[0]
    period = df["period"].iloc[0]
    source = df["source"].iloc[0]
    try:
        if not df.empty:
            result_text = [
                f"{'=' * 24}\n"
                f"股票代碼:{stock_code}\n"
                f"公司名稱:{get_stock_name(stock_code)}\n"
                f"查詢區間:{period}\n"
                f"{'=' * 24}"
            ]
            for date, row in df.iterrows():
                date = date.strftime('%Y-%m-%d')
                line = (
                    f"📅{date}\n"
                    f"📈開:{row['Open']:.2f}｜收:{row['Close']:.2f}\n"
                    f"📊高:{row['High']:.2f}｜低:{row['Low']:.2f}\n"
                    f"{'=' * 24}"
                )
                result_text.append(line)

            result_text.append(f"{source}")
            return "\n".join(result_text)
        else:
            return f"{source}無法取得股票代碼:{stock_code}"
    except Exception as e:
        return f"{e}"

#  主資料源
def get_twstock_price(stock_code):
    try:
        realtime_data = twstock.realtime.get(stock_code)
        source = "資料來源:twstock(主資料)"
        period = "1d"

        if realtime_data and realtime_data['realtime']:
            info = realtime_data.get('info', {})
            rt = realtime_data.get('realtime', {})

            df = pd.DataFrame([{
                "stock_code": stock_code,
                "period": period,
                "Date": info.get("time"),
                "Open": float(rt.get("open")),
                "Close": float(rt.get("latest_trade_price")),
                "High": float(rt.get("high")),
                "Low": float(rt.get("low")),
                "source": source,
            }])
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df.set_index("Date", inplace=True)
            return df
        else:
            return f"無法取得股票代碼{stock_code}"
    except Exception as e:
        return f"主資料源錯誤（twstock 失敗）：{e}"

#  備援資料源
def get_yfinance_price(stock_code, period):
    try:
        ticker = yfinance.Ticker(f'{stock_code}.TW')
        df = ticker.history(period= period)
        df["stock_code"] = stock_code
        df["period"] = period
        df["source"] = "資料來源:yfinance(備援資料)"
        if not df.empty:
            return df
        else:
            return f"備援資料源無法取得股票代碼{stock_code}"
    except Exception as e:
        return f"備援資料源錯誤（yfinance 失敗）：{e}"

#  美股資料源
def get_us_stock_price(stock_code, period):
    try:
        us_ticker = yfinance.Ticker(stock_code)
        us_df = us_ticker.history(period=period)
        us_df["stock_code"] = stock_code
        us_df["period"] = period
        us_df["source"] = "資料來源:yfinance(美股資料)"
        if not us_df.empty:
            return us_df
        else:
            return f"美股資料源無法取得股票代碼{stock_code}"
    except Exception as e:
        return f"美股資料源錯誤（yfinance 失敗）：{e}"

#  封裝使用的主接口（可以給 LINE Bot 使用）
def get_stock_price(user_input):
    stock_code = resolve_stock_code(user_input)
    period = parse_period(user_input)
    try:
        if stock_code.isdigit():
            if period == "1d":
                df = get_twstock_price(stock_code)
                tw_final_text = format_stock_text(df)

                if tw_final_text.startswith('無法取得') or tw_final_text.startswith("主資料源錯誤"):
                    df = get_yfinance_price(stock_code, period)
                    fallback_result = format_stock_text(df)

                    return f'主資料源錯誤，已使用備援資料\n{fallback_result}'

                return tw_final_text
            else:
                df = get_yfinance_price(stock_code, period)
                tw_period_final_text = format_stock_text(df)

                return tw_period_final_text
        elif stock_code.isalpha():
            us_df = get_us_stock_price(stock_code, period)
            us_period_final_text = format_stock_text(us_df)
            return us_period_final_text
        else:
            return (
                f'股票代碼格式錯誤:{stock_code}\n'
                f'ex:\n'
                f'台股=>2330\n'
                f'美股=>AAPL'
            )
    except Exception as e:
        return e

#  測試用
'''
test = get_stock_price(input("?:"))
print(test)
'''