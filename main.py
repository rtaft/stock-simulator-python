import mysql.connector
import yfinance as yf
import pprint
import app_config

def sync_stock_history(cursor, symbols, companies):
    for symbol in symbols:
        data = yf.Ticker(symbol)
        company = companies.get(data.info.get('fullExchangeName'), {}).get(data.info.get('symbol'))
        if not company:
            company = store_company(cursor, data)
            pprint.pprint(company)
        history = data.history(period="max")
        store_full_history(cursor, company, history)

def store_full_history(cursor, company, history):
    delete_query = 'DELETE FROM price_history WHERE company_id = {}'.format(company.get('company_id'))
    insert_query = 'INSERT INTO price_history (company_id, trade_date, trade_close, trade_volume) VALUES (%s, %s, %s, %s)'
    cursor.execute(delete_query)

    for index, row in history.iterrows():
        cursor.execute(insert_query, (company.get('company_id'), index, row['Close'], row['Volume']))

def load_companies(cursor):
    companies = dict()
    cursor.execute('SELECT * from company')
    for row in cursor:
        company = dict(company_id=row[0],
                       company_name=row[1],
                       ticker=row[2],
                       exchange=row[3],
                       cusip=row[4])
        companies.setdefault(company['exchange'], dict())[company['ticker']] = company
    return companies

def store_company(cursor, company_data):
    query = "INSERT INTO company (company_name, ticker, exchange) VALUES (%s, %s, %s)"
    data = (company_data.info.get('longName'), company_data.info.get('symbol'), company_data.info.get('fullExchangeName'))
    cursor.execute(query, data)
    return dict(company_id=cursor.lastrowid,
                company_name=company_data.info.get('longName'),
                ticker=company_data.info.get('symbol'),
                exchange=company_data.info.get('fullExchangeName'),
                cusip='')

def connect():
    return mysql.connector.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)

if __name__ == "__main__":
    symbols = ['AAPL']
    connection = connect()
    cursor = connection.cursor()
    companies = load_companies(cursor)
    sync_stock_history(cursor, symbols, companies)
    connection.commit()

    cursor.close()
    connection.close()
