import csv
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import app_config
from database.company import find_company_by_symbol
from database.stock import get_stock_list_name, add_stock_list

def import_dow(session):
    with open('csv/DJI.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            symbol = row[0]
            companies = find_company_by_symbol(session, symbol)
            matched = None
            for company in companies:
                if company['exchange'] in ['NYSE', 'NASDAQ']:
                    matched = company
                    break
            if matched:
                listing = get_stock_list_name(session, 'DOW')
                add_stock_list(session, company['company_id'], listing['list_id'])

def import_s_and_p(session):
    with open('csv/SP500.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            symbol = row[0]
            companies = find_company_by_symbol(session, symbol)
            matched = None
            for company in companies:
                if company['exchange'] in ['NYSE', 'NASDAQ']:
                    matched = company
                    break
            if matched:
                listing = get_stock_list_name(session, 'SP500')
                try:
                    date_added = datetime.datetime.strptime(row[7], '%Y-%m-%d')
                except:
                    date_added = None                
                add_stock_list(session, company['company_id'], listing['list_id'], date_added)

if __name__ == "__main__":
    engine = create_engine('{}://{}:{}@localhost/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    import_dow(session)
    import_s_and_p(session)
    session.commit()
    session.close()