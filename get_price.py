import requests
from bs4 import BeautifulSoup

def get_stock_price(stock_code):
    url = f"https://tw.stock.yahoo.com/quote/{stock_code}.TW"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    stock_name = soup.find('h1', class_="C($c-link-text) Fw(b) Fz(24px) Mend(8px)").getText()
    stock_price = soup.find('span', class_="Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-down)").getText()
    return stock_name, stock_price


