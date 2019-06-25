import sqlite3

class SQLiteDatabase:

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, database):
        self.connection = sqlite3.connect(database=database)
        self.cursor = self.connection.cursor()
        self.create_db()
        
    def create_db(self):
        install = open('database/sqlite.sql', 'r').read()
        for create in install.split(';'):
            self.cursor.execute(create)
        
    def disconnect(self):
        self.connection.disconnect()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def remove_price_history(self, company_id):
        self.cursor.execute('DELETE FROM price_history WHERE company_id = ?', (company_id,))

    def insert_price_history(self, company_id, trade_date, trade_close, trade_volume):
        query = 'INSERT INTO price_history (company_id, trade_date, trade_close, trade_volume) VALUES (?, ?, ?, ?)'
        self.cursor.execute(query, (company_id, trade_date, trade_close, trade_volume))
    
    def remove_dividend_history(self, company_id):
        self.cursor.execute('DELETE FROM dividend_history WHERE company_id = ?', (company_id,))

    def insert_dividend(self, company_id, dividend_date, dividend):
        query = 'INSERT INTO dividend_history (ex_date, dividend, company_id) VALUES (?, ?, ?)'
        self.cursor.execute(query, (dividend_date, dividend, company_id))

    def add_company_info(self, company_name, symbol, exchange, ipo, sector, industry):
        query = 'INSERT INTO company (company_name, symbol, exchange, ipo, sector, industry) VALUES (?, ?, ?, ?, ?, ?)'
        self.cursor.execute(query, (company_name, symbol, exchange, ipo, sector, industry))
        return dict(company_id=self.cursor.lastrowid,
                    company_name=company_name,
                    symbol=symbol,
                    exchange=exchange,
                    ipo=ipo,
                    sector=sector,
                    industry=industry)
    
    def get_all_companies(self):
        companies = dict()
        self.cursor.execute('SELECT * from company')
        for row in self.cursor:
            company = dict(company_id=row[0],
                        company_name=row[1],
                        symbol=row[2],
                        exchange=row[3])
            companies.setdefault(company['exchange'], dict())[company['symbol']] = company
        return companies
