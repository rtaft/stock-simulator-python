import math
import yfinance as yf
import pprint

import app_config
from database.mysql_db import MySQLDatabase

class SyncHistory:
    def __init__(self, database):
        self.database = database

    def sync_stock_history(self, symbols, companies):
        for symbol in symbols:
            data = yf.Ticker(symbol)
            company = companies.get(data.info.get('fullExchangeName'), {}).get(data.info.get('symbol'))
            if not company:
                company = self.database.add_company_info(data.info.get('longName'),
                                                         data.info.get('symbol'),
                                                         data.info.get('fullExchangeName'), 0, '', '') # TODO
                pprint.pprint(company)
            history = data.history(period="max")
            self.store_full_history(company, history)

    def store_full_history(self, company, history):
        database.remove_price_history(company_id=company.get('company_id'))
        database.remove_dividend_history(company_id=company.get('company_id'))
        for index, row in history.iterrows():
            if not math.isnan(row['Close']):
                database.insert_price_history(company.get('company_id'), index, row['Close'], row['Volume'])
            if row['Dividends']:
                database.insert_dividend(company.get('company_id'), index, row['Dividends'])

if __name__ == "__main__":
    symbols = ['BCE']
    database = MySQLDatabase()
    database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
    sync_history = SyncHistory(database)
    companies = database.get_all_companies()
    sync_history.sync_stock_history(symbols, companies)
    database.commit()