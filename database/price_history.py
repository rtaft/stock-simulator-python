from sqlalchemy import between, and_, distinct
from database.database import PriceHistory

def remove_price_history(session, company_id):
    return session.query(PriceHistory).filter(PriceHistory.company_id == company_id).delete()

def insert_price_history(session, company_id, trade_date, trade_close, trade_volume):
    session.add(PriceHistory(company_id=company_id, trade_date=trade_date, trade_close=trade_close, trade_volume=trade_volume))

def insert_price_history_bulk(session, price_history_list):
    session.add_all(price_history_list)

def get_price_history(session, company_ids=None, start_date=None, end_date=None):
    where = []
    if company_ids:
        where.append(PriceHistory.company_id.in_(company_ids))
    elif start_date and end_date:
        where.append(between(PriceHistory.trade_date, start_date, end_date))

    query = session.query(PriceHistory)
    if where:
        query = query.filter(and_(*where))
    full_history = dict()
    for price_history in query.all():
        company = full_history.setdefault(price_history.company_id, dict())
        company[price_history.trade_date] = price_history
    return full_history

def get_company_ids_in_price_history(session):
    return [row[0] for row in session.query(PriceHistory.company_id).distinct().all()]
