import datetime
import json
import requests
import yfinance
from bs4 import BeautifulSoup
import twstock
from dateutil.utils import today

with open('Taiwan Stock Exchange Popular Stock Code Comparison Table.json', "r", encoding="utf-8") as f:
    stock_name_map = json.load(f)

def get_stock_name(stock_code):
    return stock_name_map.get(stock_code, "未知公司")

'''
def get_stock_price(stock_code):
    url = f"https://tw.stock.yahoo.com/quote/{stock_code}.TW"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    stock_name = soup.find('h1', class_="C($c-link-text) Fw(b) Fz(24px) Mend(8px)").getText()
    stock_price = soup.find('span', class_="Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-down)").getText()
    return f"{stock_name} ({stock_code}) 目前股價：{stock_price}"
'''

#  資料處理工具
def remove_trailing_zero(number_str):
    if '.' in number_str:
        number_str = number_str.rstrip('0').rstrip('.')
        return number_str

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
                f"最低價:{remove_trailing_zero(rt.get('low'))}"
            )
        else:
            return f"無法取得股票代碼{stock_code}"
    except Exception as e:
        return f"主資料源錯誤（twstock 失敗）：{e}"

#  備援資料源
def get_yfinance_price(stock_code):
    try:
        today = datetime.date.today().strftime('%Y-%m-%d')
        ticker = yfinance.Ticker(f'{stock_code}.TW')
        df = ticker.history(start = today)
        if not df.empty:
            latest = df.iloc[-1]
            return (
                f"股票代碼:{stock_code}\n"
                f"公司名稱:{get_stock_name(stock_code)}\n"
                f"開盤價:{latest['Open']:.2f}\n"
                f"收盤價:{latest['Close']:.2f}\n"
                f"最高價:{latest['High']:.2f}\n"
                f"最低價:{latest['Low']:.2f}"
            )
        else:
            return f"無法取得股票代碼{stock_code}"
    except Exception as e:
        return f"備援資料源錯誤（yfinance 失敗）：{e}"

#  美股資料源
def get_us_stock_price(stock_code):
    try:
        today = datetime.date.today().strftime('%Y-%m-%d')
        us_ticker = yfinance.Ticker(stock_code)
        us_df = us_ticker.history(start= today)
        if not us_df.empty:
            us_latest = us_df.iloc[-1]
            return (
                f"股票代碼:{stock_code}\n"
                f"公司名稱:\n"
                f"開盤價:{us_latest['Open']:.2f}\n"
                f"收盤價:{us_latest['Close']:.2f}\n"
                f"最高價:{us_latest['High']:.2f}\n"
                f"最低價:{us_latest['Low']:.2f}"
            )
        else:
            return f"無法取得股票代碼{stock_code}"
    except Exception as e:
        return f"美股資料源錯誤（yfinance 失敗）：{e}"

#  封裝使用的主接口（可以給 LINE Bot 使用）
def get_stock_price(stock_code):
    match stock_code:
        case stock_code.isdigit:
            result = get_twstock_price(stock_code)
            if result.startswith('無法取得') or result.startswith("主資料源錯誤"):
                fallback_result = get_yfinance_price(stock_code)
                return f'主資料源錯誤，已使用備援資料\n{fallback_result}'
            return result
        case stock_code.isalpha:
            get_us_stock_price(stock_code)
