import math
import yfinance as yf
import app_config
from database import db
from datetime import date
class SyncDaily():

    def __init__(self, database):
        self.database = database

    def download_recent(self, start, symbols, companies, existing_history):
        data = yf.download(" ".join(symbols), start=start, end=date.today())
        for index, row in data.iterrows():
            for symbol in data.columns.levels[1]:
                if symbol in row['Close']:
                    if companies[symbol]['company_id'] not in existing_history or index.date() not in existing_history[companies[symbol]['company_id']]:
                        if not math.isnan(row['Close'][symbol]):
                            self.database.insert_price_history(companies[symbol]['company_id'], index, row['Close'][symbol], row['Volume'][symbol])
        # TODO dividends and splits

if __name__ == "__main__":
    database = db.connect()
    start = "1960-06-21"
    sync_daily = SyncDaily(database)
    companies = database.get_current_stock_list('DOW')
    history = database.get_price_history(start_date=start, end_date=date.today())
    sync_daily.download_recent(start, companies.keys(), companies, history)
    database.commit()
    database.close()