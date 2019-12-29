from sqlalchemy import between, and_, distinct
from database.database import DividendHistory
 
def remove_dividend_history(session, company_id):
    return session.query(DividendHistory).filter(DividendHistory.company_id == company_id).delete()

def insert_dividend(session, company_id, dividend_date, dividend):
    session.add(DividendHistory(company_id=company_id, dividend_date=dividend_date, dividend=dividend))

def insert_dividend_bulk(session, dividend_history_list):
    session.add_all(dividend_history_list)

def get_dividend_history(session, company_ids=None, start_date=None, end_date=None):
    where = []
    if company_ids:
        where.append(DividendHistory.company_id.in_(company_ids))
    elif start_date and end_date:
        where.append(between(DividendHistory.ex_date, start_date, end_date))

    query = session.query(DividendHistory)
    if where:
        query = query.filter(and_(*where))
    full_history = dict()
    for dividend_history in query.all():
        company = full_history.setdefault(dividend_history.company_id, dict())
        if not dividend_history.ex_date:
            print('Empty Dividend date {}'.format(dividend_history))
        elif dividend_history.ex_date not in company:
            company[dividend_history.ex_date] = dividend_history
        else:
            print('Duplicate Dividend found for {} {}'.format(dividend_history['company_id'], dividend_history['ex_date']))
    return full_history
