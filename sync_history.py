import math
import yfinance as yf
import pprint
import time
import threading

import app_config
from database.mysql_db import MySQLDatabase

class SyncHistory:
    def __init__(self, database, threads):
        self.running = True
        self.companies = None
        self.symbols = None
        self.total = 0
        self.data_to_process = []
        self.database = database
        self.threads = threads
        self.lock = threading.Lock()
        
    def process_stock_history(self, thread_id):
#        print(self.symbols)
        while self.symbols:
            print ('Progress: {}%'.format((self.total-len(self.symbols))*100//self.total), end='\r')
            symbol = symbols.pop()
            #print('Thread {} processing {}'.format(thread_id, symbol))
            self.sync_stock_history(symbol, companies)

    def sync_all_stock_history_threaded(self, symbols, companies):
        self.total = len(symbols)
        self.symbols = symbols
        self.companies = companies
        thread_list = []
        store_thread = threading.Thread(target=self.process_data_store)
        store_thread.start()
        for n in range(self.threads):
            print('Creating thread {}'.format(n))
            t = threading.Thread(target=self.process_stock_history, args=(n, ))
            t.start()
            thread_list.append(t)
        time.sleep(1)
        for t in thread_list:
            t.join()
        print ('COMPLETED DOWNLOAD')
        self.running = False
        store_thread.join()
                    
    def sync_stock_history(self, symbol, companies):
            try:
                data = yf.Ticker(symbol)
                #company = companies.get(data.info.get('fullExchangeName'), {}).get(data.info.get('symbol'))
                company = companies.get(data.info.get('symbol'))
                
                if not company:
                    print('Adding {}'.format(symbol))
                    if data.info.get('symbol'):
                        self.lock.acquire()
                        company = self.database.add_company_info(data.info.get('longName'),
                                                                 data.info.get('symbol'),
                                                                 data.info.get('fullExchangeName'), 0, '', '') # TODO
                        self.database.commit()
                        self.lock.release()
                    else:
                        return
                #else:
                #    print ("Found {}".format(data.info.get('symbol')))
                history = data.history(period="max", auto_adjust=False, rounding=False)
                self.store_full_history(company, history)
            except Exception as e:
                print('{} FAILED TO LOAD'.format(symbol))
                print(e)

    def store_full_history(self, company, history):
        data_to_store = dict(company_id=company.get('company_id'))
        price_history = []
        dividends = []
        splits = []
        history.iloc[::-1]
        multiplier = 1
        for index in reversed(history.index):
            try:
                if history.loc[index, 'Stock Splits']:
                    multiplier *= float(history.loc[index, 'Stock Splits'])
                    splits.append((company.get('company_id'), index, float(history.loc[index, 'Stock Splits'])))
                if not math.isnan(history.loc[index, 'Close']):
                    price_history.append((company.get('company_id'), index, round(float(history.loc[index, 'Close'] * multiplier), 2), int(history.loc[index, 'Volume'])))
                if history.loc[index, 'Dividends']:
                    dividends.append((company.get('company_id'), index, round(float(history.loc[index, 'Dividends'] * multiplier), 3)))
            except:
                print('Error {}'.format(company['symbol']))
                print(history.loc[index])
        data_to_store['dividends'] = dividends
        data_to_store['price_history'] = price_history
        data_to_store['splits'] = splits
        self.data_to_process.append(data_to_store)

    def process_data_store(self):
        saved = 0
        while self.running:
            if self.data_to_process:
                data = self.data_to_process.pop()
                self.store_data(data)
                saved += 1
            else:
                #print('saved {}'.format(saved))
                saved = 0
                time.sleep(1)
        print ('COMPLETED SAVING')

    def store_data(self, data):
        try:
            self.lock.acquire()
            self.database.remove_price_history(company_id=data.get('company_id'))
            self.database.remove_dividend_history(company_id=data.get('company_id'))
            self.database.remove_split_history(company_id=data.get('company_id'))
            self.database.insert_dividend_bulk(data['dividends'])
            self.database.insert_price_history_bulk(data['price_history'])
            self.database.insert_splits_bulk(data['splits'])
            self.database.commit()
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

if __name__ == "__main__":
    database = MySQLDatabase()
    database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
    sync_history = SyncHistory(database, 10)
    #companies = database.get_current_stock_list('SP500').values()
    #companies = database.get_current_stock_list('DOW')
    companies_by_exchange = database.get_companies()
    companies = dict()
    for exchange, company_dict in companies_by_exchange.items():
        companies.update(company_dict)
    print('Processing {} companies'.format(len(companies)))
    symbols = []
    ignore_company_ids = database.get_company_ids_in_price_history()
    #for symbol, company in companies.items():
    #for exchange, company_list in companies.items():
    for symbol, company in companies.items():
        if '.WS' not in symbol and '.WT' not in symbol and '.U' not in symbol and company['company_id'] not in ignore_company_ids:
            symbol = symbol.replace('.', '-')
            symbol = symbol.replace('^', '-P')
            symbol = symbol.replace('-CL', 'CL')
            symbols.append(symbol)
        #if company['symbol'] not in symbols and company['company_id'] not in ignore_company_ids:
        #    if company['symbol'] == 'BRK.B':
        #        symbols.append(symbol)
    sync_history.sync_all_stock_history_threaded(symbols, companies)
