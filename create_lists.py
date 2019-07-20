import csv
import datetime
from database import db

def import_dow(database):
    with open('csv/DJI.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            symbol = row[0]
            companies = database.find_company_by_symbol(symbol)
            matched = None
            for company in companies:
                if company['exchange'] in ['NYSE', 'NASDAQ']:
                    matched = company
                    break
            if matched:
                listing = database.get_stock_list_name('DOW')
                database.add_stock_list(company['company_id'], listing['list_id'])

def import_s_and_p(database):
    with open('csv/SP500.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            symbol = row[0]
            companies = database.find_company_by_symbol(symbol)
            matched = None
            for company in companies:
                if company['exchange'] in ['NYSE', 'NASDAQ']:
                    matched = company
                    break
            if matched:
                listing = database.get_stock_list_name('SP500')
                try:
                    date_added = datetime.datetime.strptime(row[7], '%Y-%m-%d')
                except:
                    date_added = None                
                database.add_stock_list(company['company_id'], listing['list_id'], date_added)

if __name__ == "__main__":
    database = db.connect()
    import_dow(database)
    import_s_and_p(database)
    database.commit()
    database.close()