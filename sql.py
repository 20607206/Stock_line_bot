import mysql.connector
import datetime
import pandas as pd
from dotenv import load_dotenv
import os
from stock_parser import get_yfinance_price

load_dotenv()

#  連接MySQL
def connector_mysql():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=os.getenv("MYSQL_PORT"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        return conn
    except Exception as e:
        return f"轉換錯誤: {e}"

#  Dataframe轉成SQL
def to_sql(df):
    try:
        stock_list = []
        # code = str(df["code"])
        # name = str(df["name"])
        period = df["period"].iloc[0]
        source = df["source"].iloc[0]
        time = datetime.datetime.now()
        query_time = time.strftime("%Y-%m-%d %H:%M:%S")

        for date, row in df.iterrows():
            data_date = date.strftime("%Y-%m-%d")
            stock_info = (
                row["code"],
                row["name"],
                period,
                round(row["Open"], 2),
                round(row["Close"], 2),
                round(row["High"], 2),
                round(row["Low"], 2),
                source,
                data_date,
                query_time
            )
            stock_list.append(stock_info)

        return stock_list
    except Exception  as e:
        return f"轉換錯誤: {e}"

#  存入MySQL
def save_stock_to_mysql(df):
    conn = connector_mysql()
    stock_info_list = to_sql(df)
    try:
        cursor = conn.cursor()

        sql = """
        INSERT INTO `stock_list` (`code`, `name`, `period`, `open`, `close`, `high`, `low`, `source`, `data_date`, `query_time`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for stock_info in stock_info_list:
            values = stock_info
            cursor.execute(sql, values)

    except Exception as e:
        return f"轉換錯誤: {e}"
    conn.commit()
    cursor.close()
    conn.close()

#  從MySQL提取資料
def load_stock_from_mysql(stock_code):
    conn = connector_mysql()
    cursor = conn.cursor()

    sql = "SELECT code, name, period, open, close, high, low, source, data_date, query_time FROM `stock_list` WHERE `code`= %s;"
    values = (stock_code,)

    cursor.execute(sql, values)

    record = cursor.fetchall()
    for row in record:
        df = pd.DataFrame([row], columns=('code', 'name', 'period', 'open', 'close', 'high', 'low', 'source', 'data_date', 'query_time'))
        df["data_date"] = pd.to_datetime(df["data_date"], errors="coerce")
        df.set_index("data_date", inplace=True)
        return (df)

    cursor.close()
    conn.close()

#  刪除mysql資料
def remove_sql(stock_code):
    pass
    conn = connector_mysql()
    cursor = conn.cursor()

    sql_delete = "DELETE FROM `stock_list` WHERE code= %s"
    values = (stock_code,)

    cursor.execute(sql_delete, values)

    conn.commit()
    cursor.close()
    conn.close()

# aaa = to_sql(get_yfinance_price("2330", "1d"))
# print(aaa)
# save_stock_to_mysql(aaa)

def test_mysql_connection():
    try:
        conn = connector_mysql()
        if conn.is_connected():
            print("✅ 成功連線到 MySQL 資料庫")
            conn.close()
        else:
            print("❌ 無法連線到 MySQL")
    except Exception as e:
        print(f"⚠️ 連線錯誤: {e}")

# aaa = get_yfinance_price("2330", "1d")
# print(aaa)
# bbb = to_sql(aaa)
# print(bbb)
# save_stock_to_mysql(bbb)

# load_stock_from_mysql("2330")