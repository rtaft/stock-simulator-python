import math
import yfinance as yf
import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import threading

import app_config
from database.company import add_company_info, get_companies
from database.dividend import remove_dividend_history, insert_dividend_bulk
from database.split import remove_split_history, insert_splits_bulk
from database.price_history import insert_price_history_bulk, remove_price_history, get_company_ids_in_price_history
from database.database import PriceHistory, DividendHistory, SplitHistory

class SyncHistory:
    def __init__(self, session, threads):
        self.running = True
        self.companies = None
        self.symbols = None
        self.total = 0
        self.data_to_process = []
        self.threads = threads
        self.lock = threading.Lock()
        self.session = session
        
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
                        company = add_company_info(self.session, 
                                                   data.info.get('longName'),
                                                   data.info.get('symbol'),
                                                   data.info.get('fullExchangeName'), 0, '', '') # TODO
                        self.session.commit()
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
        data_to_store = dict(company_id=company.company_id)
        price_history = []
        dividends = []
        splits = []
        history.iloc[::-1]
        multiplier = 1
        # print('STORE {}'.format(company.symbol))
        for index in reversed(history.index):
            try:
                if history.loc[index, 'Stock Splits']:
                    multiplier *= float(history.loc[index, 'Stock Splits'])
                    splits.append(SplitHistory(company_id=company.company_id, split_date=index, ratio=float(history.loc[index, 'Stock Splits'])))
                if not math.isnan(history.loc[index, 'Close']):
                    price_history.append(PriceHistory(company_id=company.company_id, 
                                                      trade_date=index,
                                                      trade_close=round(float(history.loc[index, 'Close'] * multiplier), 2),
                                                      trade_volume=int(history.loc[index, 'Volume'])))
                if history.loc[index, 'Dividends']:
                    dividends.append(DividendHistory(company_id=company.company_id, ex_date=index, dividend=round(float(history.loc[index, 'Dividends'] * multiplier), 3)))
            except:
                print('Error {}'.format(company.symbol))
                print(history.loc[index])
        print('STORE {} {}'.format(company.symbol, len(dividends)))
        data_to_store['dividends'] = dividends
        data_to_store['price_history'] = price_history
        data_to_store['splits'] = splits
        self.data_to_process.append(data_to_store)

    def process_data_store(self):
        saved = 0
        while self.running or self.data_to_process:
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
            remove_price_history(self.session, company_id=data.get('company_id'))
            remove_dividend_history(self.session, company_id=data.get('company_id'))
            remove_split_history(self.session, company_id=data.get('company_id'))
            if data['dividends']:
                insert_dividend_bulk(self.session, data['dividends'])
                self.session.commit()
            if data['price_history']:
                insert_price_history_bulk(self.session, data['price_history'])
                self.session.commit()
            if data['splits']:
                insert_splits_bulk(self.session, data['splits'])
                self.session.commit()
                
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

if __name__ == "__main__":
    engine = create_engine('{}://{}:{}@localhost/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    sync_history = SyncHistory(session, 10)
    #companies = database.get_current_stock_list('SP500').values()
    #companies = database.get_current_stock_list('DOW')
    companies_by_exchange = get_companies(session)
    companies = dict()
    for exchange, company_dict in companies_by_exchange.items():
        companies.update(company_dict)
    print('Processing {} companies'.format(len(companies)))
    symbols = []
    ignore_company_ids = get_company_ids_in_price_history(session)
    #for symbol, company in companies.items():
    #for exchange, company_list in companies.items():
    for symbol, company in companies.items():
        if '.WS' not in symbol and '.WT' not in symbol and '.U' not in symbol and company.company_id not in ignore_company_ids:
            symbol = symbol.replace('.', '-')
            symbol = symbol.replace('^', '-P')
            symbol = symbol.replace('-CL', 'CL')
            symbols.append(symbol)
        #if company['symbol'] not in symbols and company['company_id'] not in ignore_company_ids:
        #    if company['symbol'] == 'BRK.B':
        #        symbols.append(symbol)
    sync_history.sync_all_stock_history_threaded(symbols, companies)
