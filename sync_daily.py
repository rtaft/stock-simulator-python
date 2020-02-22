import math
from datetime import date
import yfinance as yf
from sqlalchemy import create_engine, and_, distinct
from sqlalchemy.orm import sessionmaker
import app_config
from database.price_history import get_price_history, insert_price_history
from database.stock import get_current_stock_list

class SyncDaily():

    def __init__(self, session):
        self.session = session

    def download_recent(self, start, symbols, companies, existing_history):
        data = yf.download(" ".join(symbols), start=start, end=date.today())
        for index, row in data.iterrows():
            for symbol in data.columns.levels[1]:
                if symbol in row['Close']:
                    if companies[symbol].company_id not in existing_history or index.date() not in existing_history[companies[symbol].company_id]:
                        if not math.isnan(row['Close'][symbol]):
                            insert_price_history(self.session, companies[symbol].company_id, index, row['Close'][symbol], row['Volume'][symbol])
        # TODO dividends and splits

if __name__ == "__main__":
    engine = create_engine('{}://{}:{}@{}/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_HOST, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    start = "2019-06-21"
    sync_daily = SyncDaily(session)
    companies = get_current_stock_list(session, 'DOW')
    history = get_price_history(session, start_date=start, end_date=date.today())
    sync_daily.download_recent(start, companies.keys(), companies, history)
    session.commit()
    session.close()