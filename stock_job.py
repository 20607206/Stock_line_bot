import time
import pandas as pd
import yfinance
import sql
import stock_parser

class StockJobManager:
    def __init__(self, stock_list):
        self.stock_list = stock_list
        self.period = "1d"


    def job1(self):
        print("Job1 is Working...")
        try:
            self.df_list = pd.DataFrame()
            for code in self.stock_list:
                df = self.get_yfinance_price(code, self.period)
                if df.empty:
                    print(f"{code} Data not found, try again in 10 seconds")
                    time.sleep(10)
                    df = self.get_yfinance_price(code, self.period)
                self.df_list = pd.concat([self.df_list, df])
            if self.df_list is not None:
                print(f"found data total:{len(self.df_list)}")
            else:
                print("No data !")
        except Exception as e:
            print(f"{e}")

    def job2(self):
        print("Job2 is Working...")
        try:
            if not self.df_list.empty:
                print("Data is being stored...")
                sql.save_stock_to_mysql(self.df_list)
                print("Storage completed")
                self.df_list = pd.DataFrame()
            else:
                print("No data !")
        except Exception as e:
            print(f"{e}")

    def job3(self):
        print("Job3 Start clearing stock data...")
        try:
            if not self.stock_list:
                print("No stock symbols to delete")
            else:
                for code in self.stock_list:
                    print(f"Starting remove {code}")
                    sql.remove_sql(code)
                    print(f"Delete code : {code}")

        except Exception as e:
            print(f"{e}")


    @staticmethod
    def get_yfinance_price(stock_code, period, is_tw=True):
        try:
            code = f"{stock_code}.TW" if is_tw else stock_code
            ticker = yfinance.Ticker(code)
            df = ticker.history(period=period)
            df["code"] = stock_code
            df["name"] = stock_parser.get_stock_name(stock_code)
            df["source"] = f"資料來源:yfinance({'台股備援' if is_tw else '美股'})"
            df["period"] = period
            pd.set_option('display.max_columns', None)
            return df
        except Exception as e:
            print(f"{e}")
            return pd.DataFrame()

    def start_schedule(self):
        print("Start Job3 ")
        self.job3()
        time.sleep(5)

        print("Start Job1 ")
        self.job1()
        time.sleep(5)

        print("Start Job2 ")
        self.job2()
        time.sleep(5)

        print("Work completed")

if __name__ == "__main__":
    stock_list = sql.user_subscribe()
    manager = StockJobManager(stock_list)
    manager.start_schedule()
