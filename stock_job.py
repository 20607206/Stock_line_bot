import logging
import json
import time
import pandas as pd
import yfinance
import sql
import stock_parser

logging.basicConfig(
    filename="info.log",
    filemode="a",
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class StockJobManager:
    def __init__(self, stock_list):
        self.stock_list = stock_list
        self.period = "1d"


    def job1(self):
        logging.info("Job1 is Working...")
        try:
            self.df_list = pd.DataFrame()
            for code in self.stock_list:
                df = self.get_yfinance_price(code, self.period)
                if df.empty:
                    logging.warning(f"{code} Data not found, try again in 10 seconds")
                    time.sleep(10)
                    df = self.get_yfinance_price(code, self.period)
                self.df_list = pd.concat([self.df_list, df])
            if self.df_list is not None:
                logging.info(f"found data total:{len(self.df_list)}")
            else:
                logging.error("No data !")
        except Exception as e:
            logging.warning(f"{e}")

    def job2(self):
        logging.info("Job2 is Working...")
        try:
            if not self.df_list.empty:
                logging.info("Data is being stored...")
                sql.save_stock_to_mysql(self.df_list)
                logging.info("Storage completed")
                self.df_list = pd.DataFrame()
            else:
                logging.error("No data !")
        except Exception as e:
            logging.warning(f"{e}", exc_info=True)

    def job3(self):
        logging.info("Job3 Start clearing stock data...")
        try:
            if not self.stock_list:
                logging.error("No stock symbols to delete")
            else:
                for code in self.stock_list:
                    logging.info(f"Starting remove {code}")
                    sql.remove_sql(code)
                    logging.info(f"Delete code : {code}")

        except Exception as e:
            logging.warning(f"{e}", exc_info=True)


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
            logging.warning(f"{e}", exc_info=True)
            return pd.DataFrame()

    def start_schedule(self):
        logging.info("Start Job3 ")
        self.job3()
        time.sleep(5)

        logging.info("Start Job1 ")
        self.job1()
        time.sleep(5)

        logging.info("Start Job2 ")
        self.job2()
        time.sleep(5)

        logging.info("Work completed")

# if __name__ == "__main__":
#     with open("stock_bidirectional_map.json", "r", encoding="utf-8") as stock:
#         maps = json.load(stock)
#         stock_list = maps['user_subscribe']
#     manager = StockJobManager(stock_list)
#     manager.start_schedule()