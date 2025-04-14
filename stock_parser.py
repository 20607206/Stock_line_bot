import datetime
import json
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

    text = text.lower()
    for name in tw_name_to_code:
        if name in text:
            tw_code = tw_name_to_code.get(name)
            return tw_code

    for name in us_name_to_code:
        if name in text:
            us_code = us_name_to_code.get(name)
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

#  處理台股編號對應名稱
def get_stock_name(stock_code):
    tw_code_to_name = maps['tw']['code_to_name']
    return tw_code_to_name.get(stock_code, "未知公司")

#  資料處理工具
def remove_trailing_zero(number_str):
    if '.' in number_str:
        number_str = number_str.rstrip('0').rstrip('.')
        return number_str

#  設定使用者搜尋天數(預設回傳1d)
def parse_period(user_input):
    period_mapping = {
        "一天": "1d",
        "一日": "1d",
        "五天": "5d",
        "五日": "5d",
        "一週": "5d",
        "一周": "5d",
        "一個月": "1mo",
        "一月": "1mo",
        "三個月": "3mo",
        "三月": "3mo",
        "半年": "6mo",
        "一年": "1y",
        "兩年": "2y"
    }
    for day in period_mapping:
        if day in user_input:
            period = period_mapping.get(day)
            return period
    return "1d"

#  主資料源
def get_twstock_price(stock_code):
    try:
        realtime_data = twstock.realtime.get(stock_code)
        if realtime_data and realtime_data['realtime']:

            info = realtime_data.get('info', {})
            rt = realtime_data.get('realtime', {})
            return (
                f"股票代碼:{info.get('code')}\n"
                f"公司名稱:{info.get(('name'))}\n"
                f"最新成交價:{remove_trailing_zero(rt.get('latest_trade_price'))}\n"
                f"開盤價:{remove_trailing_zero(rt.get('open'))}\n"
                f"最高價:{remove_trailing_zero(rt.get('high'))}\n"
                f"最低價:{remove_trailing_zero(rt.get('low'))}\n"
                f"資料來源:twstock"
            )
        else:
            return f"無法取得股票代碼{stock_code}"
    except Exception as e:
        return f"主資料源錯誤（twstock 失敗）：{e}"

#  備援資料源
def get_yfinance_price(stock_code, period):
    try:
        ticker = yfinance.Ticker(f'{stock_code}.TW')
        df = ticker.history(period= period)
        if not df.empty:
            latest = df.iloc[-1]
            return (
                f"股票代碼:{stock_code}\n"
                f"公司名稱:{get_stock_name(stock_code)}\n"
                f"開盤價:{latest['Open']:.2f}\n"
                f"收盤價:{latest['Close']:.2f}\n"
                f"最高價:{latest['High']:.2f}\n"
                f"最低價:{latest['Low']:.2f}\n"
                f"資料來源:yfinance"
            )
        else:
            return f"備援資料源無法取得股票代碼{stock_code}"
    except Exception as e:
        return f"備援資料源錯誤（yfinance 失敗）：{e}"

#  美股資料源
def get_us_stock_price(stock_code, period):
    try:
        us_ticker = yfinance.Ticker(stock_code)
        us_df = us_ticker.history(period=period)
        us_info = us_ticker.info or {}
        stock_name = us_info.get('shortName', "未知公司")
        if not us_df.empty:
            result_lines = [
                f"{'='*20}\n"
                f"股票代碼:{stock_code}\n"
                f"公司名稱:{stock_name}\n"
                f"查詢區間:{period}\n"
                f"{'='*20}"
            ]
            for date, row in us_df.iterrows():
                date_str = date.strftime('%Y-%m-%d')
                line = (f"{date_str}\n"
                        f"開:{row['Open']:.2f}\n"
                        f"收:{row['Close']:.2f}\n"
                        f"高:{row['High']:.2f}\n"
                        f"低:{row['Low']:.2f}"
                        )
                result_lines.append(line)
            result_lines.append("資料來源:yfinance")
            return "\n".join(result_lines)
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
            result = get_twstock_price(stock_code)
            if result.startswith('無法取得') or result.startswith("主資料源錯誤"):
                fallback_result = get_yfinance_price(stock_code, period)
                return f'主資料源錯誤，已使用備援資料\n{fallback_result}'
            return result
        elif stock_code.isalpha():
            us_result = get_us_stock_price(stock_code, period)
            return us_result
        else:
            return (
                f'股票代碼格式錯誤:{stock_code}\n'
                f'ex:\n'
                f'台股=>2330\n'
                f'美股=>AAPL'
            )
    except Exception as e:
        return e