import requests
from bs4 import BeautifulSoup
import twstock
'''
def get_stock_price(stock_code):
    url = f"https://tw.stock.yahoo.com/quote/{stock_code}.TW"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    stock_name = soup.find('h1', class_="C($c-link-text) Fw(b) Fz(24px) Mend(8px)").getText()
    stock_price = soup.find('span', class_="Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-down)").getText()
    return f"{stock_name} ({stock_code}) 目前股價：{stock_price}"
'''

def remove_trailing_zero(number_str):
    if '.' in number_str:
        number_str = number_str.rstrip('0').rstrip('.')
        return number_str

def get_twstock_price(stock_code):
    realtime_data = twstock.realtime.get(stock_code)

    if realtime_data and realtime_data['realtime']:
        return f"股票代碼：{realtime_data['info']['code']}\n公司名稱：{realtime_data['info']['name']}\n最新成交價：{remove_trailing_zero(realtime_data['realtime']['latest_trade_price'])}\n開盤價：{remove_trailing_zero(realtime_data['realtime']['open'])}\n最高價：{remove_trailing_zero(realtime_data['realtime']['high'])}\n最低價：{remove_trailing_zero(realtime_data['realtime']['low'])}"
    else:
        return f"無法取得股票代碼{stock_code}"
