import math
import pandas
import app_config
from database import db


class DownloadSymbols:
    def __init__(self, database):
        self.database = database
    
    def download_all(self):
        pass
    
    def import_csv(self, url, exchange, companies):
        data = pandas.read_csv(url)
        for _, row in data.iterrows():
            if row['Symbol'] not in companies.get(exchange, {}):
                ipo = 0 if math.isnan(row['IPOyear']) else row['IPOyear']
                industry = '' if not isinstance(row['Industry'],str) else row['Industry']
                sector = '' if not isinstance(row['Sector'], str) else row['Sector']
                self.database.add_company_info(row['Name'], row['Symbol'], exchange, ipo, industry, sector)

if __name__ == "__main__":
    database = db.connect()
    sync_daily = DownloadSymbols(database)
    companies = database.get_all_companies()
    sync_daily.import_csv('http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE&render=download', 'NYSE', companies)
    sync_daily.import_csv('http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&render=download', 'NASDAQ', companies)
    database.commit()
    database.close()
