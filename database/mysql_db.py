import mysql.connector

class MySQLDatabase:

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, user, password, database):
        self.connection = mysql.connector.connect(user=user, password=password, database=database)
        self.cursor = self.connection.cursor()
    
    def disconnect(self):
        self.connection.disconnect()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def remove_price_history(self, company_id):
        self.cursor.execute('DELETE FROM price_history WHERE company_id = {}'.format(company_id))

    def insert_price_history(self, company_id, trade_date, trade_close, trade_volume):
        query = 'INSERT INTO price_history (company_id, trade_date, trade_close, trade_volume) VALUES (%s, %s, %s, %s)'
        self.cursor.execute(query, (company_id, trade_date, trade_close, trade_volume))
    
    def insert_price_history_bulk(self, bulk_data):
        """
            :param bulk_data: List of tuples using  (company_id, trade_date, trade_close, trade_volume)
        """
        query = 'INSERT INTO price_history (company_id, trade_date, trade_close, trade_volume) VALUES (%s, %s, %s, %s)'
        self.cursor.executemany(query, bulk_data)

    def get_price_history(self, company_ids=None, start_date=None, end_date=None):
        """
            dict[company_id][trade_date][history object]
        """
        if company_ids:
            self.cursor.execute('SELECT * FROM price_history where company_id in ({})'.format(', '.join(['%s']*len(company_ids))), company_ids)
        elif start_date and end_date:
            self.cursor.execute('SELECT * FROM price_history where trade_date BETWEEN %s AND %s', (start_date, end_date))
        else:
            self.cursor.execute('SELECT * FROM price_history')
        full_history = dict()
        for row in self.cursor:
            price_history = dict(history_id=row[0], company_id=row[1], trade_date=row[2], trade_close=row[3], trade_volume=row[4])
            company = full_history.setdefault(price_history['company_id'], dict())
            company[price_history['trade_date']] = price_history
        return full_history

    def get_company_ids_in_price_history(self):
        self.cursor.execute('SELECT DISTINCT company_id FROM price_history')
        company_ids = []
        for row in self.cursor:
            company_ids.append(row[0])
        return company_ids

    def remove_dividend_history(self, company_id):
        self.cursor.execute('DELETE FROM dividend_history WHERE company_id = {}'.format(company_id))

    def insert_dividend(self, company_id, dividend_date, dividend):
        query = 'INSERT INTO dividend_history (company_id, ex_date, dividend) VALUES (%s, %s, %s)'
        self.cursor.execute(query, (company_id, dividend_date, dividend))

    def insert_dividend_bulk(self, bulk_data):
        """
            :param bulk_data: List of tuples using  (dividend_date, dividend, company_id)
        """
        query = 'INSERT INTO dividend_history (company_id, ex_date, dividend) VALUES (%s, %s, %s)'
        self.cursor.executemany(query, bulk_data)

    def get_dividend_history(self, company_ids=None, start_date=None, end_date=None):
        if company_ids:
            self.cursor.execute('SELECT * FROM dividend_history where company_id in ({})'.format(', '.join(['%s']*len(company_ids))), company_ids)
        elif start_date and end_date:
            self.cursor.execute('SELECT * FROM dividend_history where ex_date BETWEEN %s AND %s', (start_date, end_date))
        else:
            self.cursor.execute('SELECT * FROM dividend_history')
        full_history = dict()
        for row in self.cursor:
            dividend_history = dict(dividend_id=row[0], company_id=row[1], ex_date=row[2], dividend=row[3])
            company = full_history.setdefault(dividend_history['company_id'], dict())
            if not dividend_history['ex_date']:
                print('Empty Dividend date {}'.format(dividend_history))
            elif dividend_history['ex_date'] not in company:
                company[dividend_history['ex_date']] = dividend_history
            else:
                print('Duplicate Dividend found for {} {}'.format(dividend_history['company_id'], dividend_history['ex_date']))
        return full_history

    def insert_splits_bulk(self, bulk_data):
        query = 'INSERT INTO split_history (company_id, split_date, ratio) VALUES (%s, %s, %s)'
        self.cursor.executemany(query, bulk_data)

    def insert_split(self, company_id, split_date, ratio):
        query = 'INSERT INTO split_history (company_id, split_date, ratio) VALUES (%s, %s, %s)'
        self.cursor.execute(query, (company_id, split_date, ratio))

    def get_split_history(self, company_ids=None, start_date=None, end_date=None):
        if company_ids:
            self.cursor.execute('SELECT * FROM split_history where company_id in ({})'.format(', '.join(['%s']*len(company_ids))), company_ids)
        elif start_date and end_date:
            self.cursor.execute('SELECT * FROM split_history where split_date BETWEEN %s AND %s', (start_date, end_date))
        else:
            self.cursor.execute('SELECT * FROM split_history')
        full_history = dict()
        for row in self.cursor:
            split_history = dict(split_id=row[0], company_id=row[1], split_date=row[2], ratio=row[3])
            company = full_history.setdefault(split_history['company_id'], dict())
            if not split_history['split_date']:
                print('Empty split date {}'.format(split_history))
            elif split_history['split_date'] not in company:
                company[split_history['split_date']] = split_history
            else:
                print('Duplicate split found for {} {}'.format(split_history['company_id'], split_history['split_date']))
        return full_history

    def remove_split_history(self, company_id):
        self.cursor.execute('DELETE FROM split_history WHERE company_id = {}'.format(company_id))

    def add_company_info(self, company_name, symbol, exchange, ipo, sector, industry):
        query = 'INSERT INTO company (company_name, symbol, exchange, ipo, sector, industry) VALUES (%s, %s, %s, %s, %s, %s)'
        self.cursor.execute(query, (company_name, symbol, exchange, ipo, sector, industry))
        return dict(company_id=self.cursor.lastrowid,
                    company_name=company_name,
                    symbol=symbol,
                    exchange=exchange,
                    ipo=ipo,
                    sector=sector,
                    industry=industry)
    
    def get_companies(self, company_ids=None):
        companies = dict()
        if company_ids:
            self.cursor.execute('SELECT * from company WHERE company_id in ({})'.format(', '.join(['%s']*len(company_ids))), company_ids)
        else:
            self.cursor.execute('SELECT * from company')
        for row in self.cursor:
            company = dict(company_id=row[0],
                        company_name=row[1],
                        symbol=row[2],
                        exchange=row[3])
            companies.setdefault(company['exchange'], dict())[company['symbol']] = company
        return companies

    def get_companies_by_id(self, company_ids=None):
        companies = dict()
        if company_ids:
            self.cursor.execute('SELECT * from company WHERE company_id in ({})'.format(', '.join(['%s']*len(company_ids))), company_ids)
        else:
            self.cursor.execute('SELECT * from company')
        for row in self.cursor:
            company = dict(company_id=row[0],
                        company_name=row[1],
                        symbol=row[2],
                        exchange=row[3])
            companies[row[0]] = company
        return companies
    
    def find_company_by_symbol(self, symbol):
        companies = []
        self.cursor.execute('SELECT * from company where symbol = %s', (symbol, ))
        for row in self.cursor:
            company = dict(company_id=row[0],
                           company_name=row[1],
                           symbol=row[2],
                           exchange=row[3])
            companies.append(company)
        return companies

    def get_stock_list_name(self, name):
        self.cursor.execute('SELECT * from stock_list where name = %s', (name, ))
        row = self.cursor.fetchone()
        if row:
            return dict(list_id=row[0], name=name)
        self.cursor.execute('INSERT INTO stock_list VALUES (%s, %s)', (None, name))
        return dict(list_id=self.cursor.lastrowid, name=name)
    
    def add_stock_list(self, company_id, list_id, start_date=None, end_date=None):
        self.cursor.execute('INSERT INTO stock_list_data VALUES (%s, %s, %s, %s)', (company_id, list_id, start_date, end_date))

    def get_current_stock_list(self, name):
        self.cursor.execute('SELECT * from company where company_id in (SELECT company_id FROM stock_list_data where list_id = '\
            '(SELECT list_id from stock_list where name = %s) AND date_removed IS NULL)', (name, ))
        companies = dict()
        for row in self.cursor:
            company = dict(company_id=row[0],
                           company_name=row[1],
                           symbol=row[2],
                           exchange=row[3])
            companies[company['symbol']] = company
        return companies

    def get_traders(self, trader_ids=None):
        if trader_ids:
            #traders.select().where(trader_id=trader_ids)
            print('SELECT * FROM traders WHERE trader_id IN ({})'.format(', '.join(['%s']*len(trader_ids))))
            self.cursor.execute('SELECT * FROM traders WHERE trader_id IN ({})'.format(', '.join(['%s']*len(trader_ids))), trader_ids)
        else:
            self.cursor.execute('SELECT * FROM traders')
        traders = []
        for row in self.cursor:
            trader = dict(trader_id=row[0],
                          name=row[1],
                          location=row[2])
            traders.append(trader)
        return traders

    def add_trader(self, name, location):
        self.cursor.execute('INSERT INTO traders (name, location) VALUES (%s, %s)', (name, location))
    
    def edit_trader(self, trader_id, name):
        self.cursor.execute('UPDATE traders set name = %s where trader_id = %s', (name, trader_id))
    
    def delete_trader(self, trader_id):
        self.cursor.execute('DELETE FROM traders WHERE trader_id = %s', (trader_id))

    def add_simulation(self, start_date, end_date, starting_balance, simulation_date, trader_id, description):
        self.cursor.execute('INSERT INTO simulation (start_date, end_date, starting_balance, simulation_date, trader_id, description) VALUES (%s, %s, %s, %s, %s, %s)', 
                            (start_date, end_date, starting_balance, simulation_date, trader_id, description))
        return self.cursor.lastrowid
    
    def add_transaction(self, simulation_id, transaction_date, transaction_quantity, transaction_price, transaction_type, symbol):
        self.cursor.execute('INSERT INTO transaction (simulation_id, transaction_date, transaction_quantity, transaction_price, transaction_type, symbol) values (%s, %s, %s, %s, %s, %s)',
                             (simulation_id, transaction_date, transaction_quantity, transaction_price, transaction_type, symbol))
        return self.cursor.lastrowid