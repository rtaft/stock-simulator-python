import math
import yfinance as yf
import pprint
import time

import app_config
from database.mysql_db import MySQLDatabase

class SyncHistory:
    def __init__(self, database):
        self.database = database

    def sync_stock_history(self, symbols, companies):
        for symbol in symbols:
            data = yf.Ticker(symbol)
            #company = companies.get(data.info.get('fullExchangeName'), {}).get(data.info.get('symbol'))
            company = companies.get(data.info.get('symbol'))
            if not company:
                company = self.database.add_company_info(data.info.get('longName'),
                                                         data.info.get('symbol'),
                                                         data.info.get('fullExchangeName'), 0, '', '') # TODO
                pprint.pprint(company)
            else:
                print ("Found {}".format(data.info.get('symbol')))
            history = data.history(period="max", auto_adjust=False)
            self.store_full_history(company, history)

    def store_full_history(self, company, history):
        database.remove_price_history(company_id=company.get('company_id'))
        database.remove_dividend_history(company_id=company.get('company_id'))
        price_history = []
        dividends = []
        splits = []
        history.iloc[::-1]
        multiplier = 1
        for index in reversed(history.index):
            if history.loc[index, 'Stock Splits']:
                multiplier *= float(history.loc[index, 'Stock Splits'])
                splits.append((company.get('company_id'), index, float(history.loc[index, 'Stock Splits'])))
            if not math.isnan(history.loc[index, 'Close']):
                price_history.append((company.get('company_id'), index, round(float(history.loc[index, 'Close'] * multiplier), 2), int(history.loc[index, 'Volume'])))
            if history.loc[index, 'Dividends']:
                dividends.append((company.get('company_id'), index, round(float(history.loc[index, 'Dividends'] * multiplier), 3)))
            
        database.insert_dividend_bulk(dividends)
        database.insert_price_history_bulk(price_history)
        database.insert_splits_bulk(splits)

if __name__ == "__main__":
    database = MySQLDatabase()
    database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
    sync_history = SyncHistory(database)
    companies = database.get_current_stock_list('DOW')
    symbols = []
    ignore_company_ids = database.get_company_ids_in_price_history()
    for symbol, company in companies.items():
        if company['symbol'] not in symbols and company['company_id'] not in ignore_company_ids:
            symbols.append(company['symbol'])
    sync_history.sync_stock_history(symbols, companies)
    database.commit()