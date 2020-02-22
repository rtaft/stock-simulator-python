import argparse
import math
import yfinance as yf
import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import time
import threading

import app_config
from database.company import add_company_info, get_companies, get_companies_by_id
from database.dividend import remove_dividend_history, insert_dividend_bulk
from database.split import remove_split_history, insert_splits_bulk
from database.price_history import insert_price_history_bulk, remove_price_history, get_company_ids_in_price_history
from database.database import PriceHistory, DividendHistory, SplitHistory
from database.stock import get_current_stock_list

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
        self.companies_to_add = []
        self.errors = []
        
    def process_stock_history(self, thread_id):
#        print(self.symbols)
        while self.symbols:
            print ('Progress: {}%'.format((self.total-len(self.symbols))*100//self.total), end='\r')
            symbol = symbols.pop()
            if DEBUG >= 2:
                print('Thread {} processing {}'.format(thread_id, symbol))
            self.sync_stock_history(symbol, self.companies)

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

        print('Missing companies:')
        for company in self.companies_to_add:
            print (company)

        
    def sync_stock_history(self, symbol, companies):
            try:
                data = yf.Ticker(symbol)
                company = companies.get(symbol)
                if not company:
                    print('Missing {}'.format(symbol))
                    self.companies_to_add.append(dict(name=data.info.get('longName'), symbol=symbol, exchange=data.info.get('fullExchangeName')))
                    return
#                    if data.info.get('symbol'):
#                        self.lock.acquire()
#                        company = add_company_info(self.session, 
#                                                   data.info.get('longName'),
#                                                   data.info.get('symbol'),
#                                                   data.info.get('fullExchangeName'), 0, '', '') # TODO
#                        self.session.commit()
#                        self.lock.release()
#                    else:
#                        return
                #else:
                #    print ("Found {}".format(data.info.get('symbol')))
                history = data.history(period="max", auto_adjust=False, rounding=False)
                if len(history):
                    self.store_full_history(company, history)
                else:
                    self.errors.append(company)
            except Exception as e:
                print('{} FAILED TO LOAD: {}'.format(symbol, str(e)))
                if '404' in str(e):
                    time.sleep(5)
                    
    def store_full_history(self, company, history):
        data_to_store = dict(company_id=company['company_id'], symbol=company['symbol'])
        price_history = []
        dividends = []
        splits = []
        history.iloc[::-1]
        multiplier = 1

        for index in reversed(history.index):
            try:
                if history.loc[index, 'Stock Splits']:
                    multiplier *= float(history.loc[index, 'Stock Splits'])
                    splits.append(dict(company_id=company['company_id'], split_date=index, ratio=float(history.loc[index, 'Stock Splits'])))
                if not math.isnan(history.loc[index, 'Close']):
                    price_history.append(dict(company_id=company['company_id'], 
                                              trade_date=index,
                                              trade_close=round(float(history.loc[index, 'Close'] * multiplier), 2),
                                              trade_volume=int(history.loc[index, 'Volume'])))
                if history.loc[index, 'Dividends']:
                    dividends.append(dict(company_id=company['company_id'], ex_date=index, dividend=round(float(history.loc[index, 'Dividends'] * multiplier), 3)))
            except:
                print('Error {}'.format(company['symbol']))
                print(history.loc[index])
        if DEBUG >= 2:
            print('QUEUED {} {} {} {}'.format(company['symbol'], len(price_history), len(dividends), len(splits)))
        data_to_store['dividends'] = dividends
        data_to_store['price_history'] = price_history
        data_to_store['splits'] = splits
        self.data_to_process.append(data_to_store)

    def process_data_store(self):
        saved = 0
        while self.running or self.data_to_process:
            if self.errors:
                company_ids = []
                while self.errors:
                    company_ids.append(self.errors.pop()['company_id'])
                companies = get_companies_by_id(self.session, company_ids)
                for company in companies.values():
                    company.error = 'X'
                self.session.commit()

            if self.data_to_process:
                data = self.data_to_process.pop()
                self.store_data(data)
                saved += 1
            else:
                if DEBUG >= 2:
                    print('saved {}'.format(saved))
                saved = 0
                time.sleep(1)
        print ('COMPLETED SAVING')

    def store_data(self, data):
        try:
            if DEBUG >= 2:
                print('STORE {} {}'.format(data['symbol'], len(self.data_to_process)))
            start = time.time()
            remove_price_history(self.session, company_id=data.get('company_id'))
            remove_dividend_history(self.session, company_id=data.get('company_id'))
            remove_split_history(self.session, company_id=data.get('company_id'))
            self.session.commit()
            if data['dividends']:
                insert_dividend_bulk(self.session, data['dividends'])
                self.session.commit()
            if data['price_history']:
                insert_price_history_bulk(self.session, data['price_history'])
                self.session.commit()
            if data['splits']:
                insert_splits_bulk(self.session, data['splits'])
                self.session.commit()
            end = time.time()
            delta = end - start
            if DEBUG >= 2:
                print ("{} took {:.2f} seconds to process".format(data['symbol'], delta))
        except Exception as e:
            print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrapes stocks from yahoo finance and stores it')
    parser.add_argument('-d', '--debug', dest='debug', type=int, default=0, help='Debug level 0-3')
    parser.add_argument('-p', '--purge', dest='purge', action='store_true', default=False, help='Purge data already in the database.')
    parser.add_argument('-l', '--list', dest='stock_list', type=str, default='ALL', help='Loads data for the specified stock list.')
    parser.add_argument('-t', '--threads', dest='threads', type=int, default=5, help='Number of download threads.')
    
    args = parser.parse_args(sys.argv[1:])

    DEBUG = args.debug
    if DEBUG >= 3:
        import logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    
    engine = create_engine('{}://{}:{}@{}/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_HOST, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    sync_history = SyncHistory(session, args.threads)

    if args.stock_list == 'ALL':
        temp_companies = dict()
        for exchange, company_dict in get_companies(session).items():
            temp_companies.update(company_dict)
    else:
        temp_companies = get_current_stock_list(session, args.stock_list)

    error_count = 0
    companies = dict()
    for symbol, company in temp_companies.items():
        if not company.error:
            companies[symbol] = dict(company.__dict__)
            del companies[symbol]['_sa_instance_state']
        else:
            error_count += 1
            
    print('Processing {} companies, removed {} errors.'.format(len(companies), error_count))
    symbols = []
    if args.purge:
        ignore_company_ids = []
    else:
        ignore_company_ids = get_company_ids_in_price_history(session)

    # This attempts to convert symbols to ones that match Yahoos listings.
    for symbol, company in companies.items():
        if '.WS' not in symbol and '.WT' not in symbol and '.U' not in symbol and company['company_id'] not in ignore_company_ids:
            symbol = symbol.replace('.', '-')
            symbol = symbol.replace('^', '-P')
            symbol = symbol.replace('-CL', 'CL')
            symbols.append(symbol)

    sync_history.sync_all_stock_history_threaded(symbols, companies)
