import math
import pandas
import app_config
from sqlalchemy import between, and_, distinct
from database.company import add_company_info, get_companies


class DownloadSymbols:
    def __init__(self, session):
        self.session = session
    
    def download_all(self):
        pass
    
    def import_csv(self, url, exchange, companies):
        data = pandas.read_csv(url)
        for _, row in data.iterrows():
            if row['Symbol'] not in companies.get(exchange, {}):
                ipo = 0 if math.isnan(row['IPOyear']) else row['IPOyear']
                industry = '' if not isinstance(row['Industry'],str) else row['Industry']
                sector = '' if not isinstance(row['Sector'], str) else row['Sector']
                add_company_info(self.session, row['Name'], row['Symbol'], exchange, ipo, industry, sector)

if __name__ == "__main__":
    engine = create_engine('{}://{}:{}@localhost/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    #database = MySQLDatabase()
    #database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
    #database = db.connect()
    sync_daily = DownloadSymbols(session)
    companies = get_companies(session)
    sync_daily.import_csv('http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE&render=download', 'NYSE', companies)
    sync_daily.import_csv('http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&render=download', 'NASDAQ', companies)
    session.commit()
    session.close()
