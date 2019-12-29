from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app_config
from database.price_history import get_price_history

def main():
    engine = create_engine('{}://{}:{}@localhost/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    companies = database.get_companies_by_id()
    for company_id, company in companies.items():
        price_history = get_price_history(session, company_ids=[company_id])
        split_history = database.get_split_history()
        if price_history:
            history = price_history[company_id]
            last_value = -1
            last_date = -1
            for trade_date in sorted(list(history.keys())):
                value = history[trade_date]
                if last_value != -1:
                    if value.trade_close == 0 or last_value / value.trade_close > 100:
                        print('{} Bad data {} / {} on {} - {}'.format(company['symbol'], last_value, value.trade_close, last_date, trade_date))
                        break
                    #if value.trade_volume:
                    #    print('No Volume for {} on {}'.format(company['symbol'], trade_date))
                    #    break
                last_value = value.trade_close
                last_date = trade_date


if __name__ == "__main__":
    main()
