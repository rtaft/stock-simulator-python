import math
import pandas
import app_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import between, and_, distinct
from database.company import add_company_info, get_companies


class DownloadSymbols:
    def __init__(self, session):
        self.session = session
    
    def download_all(self):
        pass
    
    def import_csv_old(self, url, exchange, companies):
        data = pandas.read_csv(url)
        for _, row in data.iterrows():
            if row['Symbol'] not in companies.get(exchange, {}):
                ipo = 0 if math.isnan(row['IPOyear']) else row['IPOyear']
                industry = '' if not isinstance(row['Industry'],str) else row['Industry']
                sector = '' if not isinstance(row['Sector'], str) else row['Sector']
                add_company_info(self.session, row['Name'], row['Symbol'], exchange, ipo, industry, sector)
    
    def import_csv(self, url, exchange, companies):
        data = pandas.read_csv(filepath_or_buffer=url, sep='|', usecols=[2,10], skipfooter=1)
        #print(data)
        for _, row in data.iterrows():
            if row['NASDAQ Symbol'] not in companies.get(exchange, {}):
                ipo = 0 #if math.isnan(row['IPOyear']) else row['IPOyear']
                industry = '' #if not isinstance(row['Industry'],str) else row['Industry']
                sector = '' #if not isinstance(row['Sector'], str) else row['Sector']
                #name = ((row['Security Name'][:95]) if len(row['Security Name']) > 98 else row['Security Name'])
                #print(_)
                add_company_info(self.session, row['Security Name'][:100], row['NASDAQ Symbol'], exchange, ipo, industry, sector)

if __name__ == "__main__":
    engine = create_engine('{}://{}:{}@localhost/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    #database = MySQLDatabase()
    #database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
    #database = db.connect()
    downloader = DownloadSymbols(session)
    companies = get_companies(session)
    #downloader.import_csv('http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE&render=download', 'NYSE', companies)
    #downloader.import_csv('http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&render=download', 'NASDAQ', companies)
    downloader.import_csv('ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt', 'NASDAQ', companies)
    session.commit()
    session.close()
