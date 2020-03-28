import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app_config
from database.price_history import get_price_history
from database.split import get_split_history
from database.company import get_companies_by_id
from price_history_manager import PriceHistoryManager
def main():
    engine = create_engine('{}://{}:{}@{}/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_HOST, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    companies = get_companies_by_id(session)
    price_history = PriceHistoryManager(session, load_size=1, company_ids=companies.keys())
    split_history = get_split_history(session)
    #print(split_history)
    bad_companies = dict()
    for year in range(1980, 2020):
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year+1, 1, 1)
        price_history.clear()
        price_history.initial_load(past_days=366, current_date=end_date)
        print('Testing {}'.format(year))
        for company_id, company in companies.items():
            history = price_history.get_price_history(company_id=company_id, start_date=start_date, end_date=end_date)
            #print(history)
            #print('Checking {} {}'.format(year, company.symbol))
            last_value = -1
            last_date = -1
            bad_count = 0
            for trade_date in sorted(list(history.keys())):
                value = history[trade_date]
                #print(value)
                if last_value != -1:
                    if value.trade_close == 0 or (last_value / value.trade_close) > 10 or (last_value / value.trade_close) < 0.1:
                        if not split_history.get(company_id, {}).get(last_date) and not split_history.get(company_id, {}).get(trade_date):
                            #print('{} Bad data {} / {} on {} - {}'.format(company.symbol, last_value, value.trade_close, last_date, trade_date))
                            bad_count += 1
                    #if value.trade_volume:
                    #    print('No Volume for {} on {}'.format(company['symbol'], trade_date))
                    #    break
                last_value = value.trade_close
                last_date = trade_date
            if bad_count:
                total = bad_companies.setdefault(company, 0)
                bad_companies[company] = total + bad_count
                print('Bad Count {} {} {}'.format(year, company.symbol, bad_count))
    
    for company, count in bad_companies.items():
        print('Bad Count {} {}'.format(company.symbol, count))
        if count > 5:
            company.error = 'D'
    session.commit()


if __name__ == "__main__":
    main()
