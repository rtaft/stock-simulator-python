import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app_config
from database.price_history import get_price_history
from database.split import get_split_history
from database.company import get_companies_by_id



def is_close(left, right):
    return 0.90 < (left / right) < 1.1

def main():
    engine = create_engine('{}://{}:{}@{}/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_HOST, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    companies = get_companies_by_id(session)
    # compnay_id, date, split data
    split_history = get_split_history(session)
    bucket = []
    for company_id, company in companies.items():
        split_data =split_history.get(company_id)
        if split_data:
            for split_date, split in split_data.items():
                last_value = -1
                last_date = -1
                end_date = split_date
                price_history = get_price_history(session, [company_id], split_date-datetime.timedelta(days=4), split_date+datetime.timedelta(days=4))
                trade_dates = sorted(price_history[company_id].keys())
                for trade_date in trade_dates:
                    if last_date != -1 and trade_date >= split_date:
                        end_date = trade_date
                        if end_date != split_date:
                            split.adjusted_date = end_date
                            print('Moving Split date {} to {} for {}'.format(split_date, end_date, company.symbol))
                        break
                    last_date = trade_date
                try:
                    if not is_close(price_history[company_id][last_date].trade_close * split.ratio, price_history[company_id][end_date].trade_close):
                        for trade_date in trade_dates:
                            trade = price_history[company_id][trade_date]
                            if last_value != -1:
                                if is_close(last_value * split.ratio, trade.trade_close):
                                    if split_date != trade_date and (trade.company_id,trade.trade_date) not in bucket:
                                        split.adjusted_date = trade_date
                                        print("Correct {} from {} vs {}".format(company.symbol, split_date, trade_date))
                                        break
                                    bucket.append((trade.company_id,trade.trade_date))
                            last_value = trade.trade_close
                except Exception:
                    print('{} {} {}'.format(company_id, last_date, split_date))
                    exit(1)
    session.commit()


if __name__ == "__main__":
    main()
