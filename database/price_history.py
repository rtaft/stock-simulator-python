from sqlalchemy import between, and_, distinct
from database.database import t_price_history

def remove_price_history(session, company_id):
    return session.execute(t_price_history.delete().where(t_price_history.c.company_id == company_id))

def insert_price_history(session, company_id, trade_date, trade_close, trade_volume):
    session.execute(t_price_history.insert().values(company_id=company_id, trade_date=trade_date, trade_close=trade_close, trade_volume=trade_volume))
    
def insert_price_history_bulk(session, price_history_list):
    session.execute(t_price_history.insert(), price_history_list)
    
def get_price_history(session, company_ids=None, start_date=None, end_date=None):
    where = []
    if company_ids:
        where.append(t_price_history.c.company_id.in_(company_ids))
    
    if start_date and end_date:
        if start_date == end_date:
            where.append(t_price_history.c.trade_date == start_date)
        else:
            where.append(between(t_price_history.c.trade_date, start_date, end_date))

    query = t_price_history.select()
    if where:
        query = query.where(and_(*where))
    full_history = dict()
    for price_history in session.execute(query):
        company = full_history.setdefault(price_history.company_id, dict())
        company[price_history.trade_date] = price_history
    return full_history

def get_company_ids_in_price_history(session):
    return [row[0] for row in session.query(t_price_history.c.company_id).distinct().all()]
