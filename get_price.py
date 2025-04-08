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


def get_twstock_price(stock_code):
    realtime_data = twstock.realtime.get(stock_code)

    if realtime_data and realtime_data['realtime']:
        return (f"股票代碼：{realtime_data['info']['code']}\n",
               f"公司名稱：{realtime_data['info']['name']}\n",
               f"最新成交價：{realtime_data['realtime']['latest_trade_price']}\n",
               f"開盤價：{realtime_data['realtime']['open']}\n",
               f"最高價：{realtime_data['realtime']['high']}\n",
               f"最低價：{realtime_data['realtime']['low']}")
    else:
        print(f"無法取得股票代碼{stock_code}")
