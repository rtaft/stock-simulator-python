from database.mysql_db import MySQLDatabase

import app_config

def main():
    database = MySQLDatabase()
    database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
    companies = database.get_companies_by_id()
    for company_id, company in companies.items():
        price_history = database.get_price_history(company_ids=[company_id])
        if price_history:
            history = price_history[company_id]
            last_value = -1
            last_date = -1
            for trade_date in sorted(list(history.keys())):
                value = history[trade_date]
                if last_value != -1:
                    if value['trade_close'] == 0 or last_value / value['trade_close'] > 100:
                        print('{} Bad data {} / {} on {} - {}'.format(company['symbol'], last_value, value['trade_close'], last_date, trade_date))
                        break
                    #if value['trade_volume']:
                    #    print('No Volume for {} on {}'.format(company['symbol'], trade_date))
                    #    break
                last_value = value['trade_close']
                last_date = trade_date


if __name__ == "__main__":
    main()
