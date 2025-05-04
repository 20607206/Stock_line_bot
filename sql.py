import mysql.connector
import datetime
import pandas as pd
from dotenv import load_dotenv
import os

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
        print(f"MySQL連線錯誤：{e}")
        return None

#  Dataframe轉成SQL
def to_sql(df):
    try:
        stock_list = []
        # code = str(df["code"])
        # name = str(df["name"])
        period = df["period"].iloc[0]
        source = "Data source:MYSQL(DataBase)"
        tw_time = datetime.timezone(datetime.timedelta(hours=8))
        time = datetime.datetime.now()
        query_time = time.now(tz=tw_time).strftime("%Y-%m-%d %H:%M:%S")

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
        print(f"轉換錯誤: {e}")
        return None

#  存入MySQL
def save_stock_to_mysql(df):
    conn = connector_mysql()
    stock_info_list = to_sql(df)
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO `stock_list` (`code`, `name`, `period`, `Open`, `Close`, `High`, `Low`, `source`, `data_date`, `query_time`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for stock_info in stock_info_list:
            values = stock_info
            cursor.execute(sql, values)
        print("儲存成功")
    except Exception as e:
        print(f"存入失敗: {e}")
    finally:
        conn.commit()
        cursor.close()
        conn.close()

#  從MySQL提取資料
def load_stock_from_mysql(stock_code, period):
    from stock_parser import get_stock_data
    conn = connector_mysql()
    cursor = conn.cursor()
    try:
        sql = ("SELECT code, name, period, Open, Close, High, Low, source, data_date, query_time "
               "FROM `stock_list` "
               "WHERE `code`= %s AND `period`= %s"
               "ORDER BY data_date DESC;")
        values = (stock_code, period,)
        cursor.execute(sql, values)
        record = cursor.fetchall()

        if not record:
            df = get_stock_data(stock_code, period)
            save_stock_to_mysql(df)
            subscribe_stock(stock_code)
            return df
        else:
            for row in record:
                df = pd.DataFrame([row], columns=(
                    'code', 'name', 'period', 'Open', 'Close', 'High', 'Low', 'source', 'data_date', 'query_time'
                ))
                df["data_date"] = pd.to_datetime(df["data_date"], errors="coerce")
                df.set_index("data_date", inplace=True)
                return (df)
    except Exception as e:
        print(f"提取失敗:{e}")
        return None

    finally:
        cursor.close()
        conn.close()

#  刪除mysql資料
def remove_sql(stock_code):
    conn = connector_mysql()
    cursor = conn.cursor()
    try:
        sql_delete = "DELETE FROM `stock_list` WHERE code= %s"
        values = (stock_code,)

        cursor.execute(sql_delete, values)
    except Exception as e:
        print(f"刪除失敗{e}")
        return None
    finally:
        conn.commit()
        cursor.close()
        conn.close()

#  股票列表
def user_subscribe():
    conn = connector_mysql()
    cursor = conn.cursor()
    try:
        user_subscribe = ("SELECT `code` "
                          "FROM user_subscribe")
        cursor.execute(user_subscribe)
        result = cursor.fetchall()
        subscribe_list = [row[0] for row in result]
        return subscribe_list
    except Exception as e:
        print(f"提取失敗{e}")
        return None
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def subscribe_stock(stock_code):
    conn = connector_mysql()
    cursor = conn.cursor()
    try:
        subscribe ='''
        INSERT INTO `user_subscribe` (`code`)"
        values (%s)
        '''
        cursor.execute(subscribe, list(stock_code))
        print("訂閱成功!!")
    except Exception as e:
        print(f"訂閱失敗{e}")
        return None
    finally:
        conn.commit()
        cursor.close()
        conn.close()
#  測試連線
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
