from sqlalchemy import between, and_, distinct
from database.database import StockList, StockListDatum, Company

def get_stock_list_name(session, name):
    stock_list = session.query(StockList).filter(StockList.name == name).one_or_none()
    if stock_list:
        return stock_list
    stock_list = StockList(name=name)
    session.add(stock_list)
    session.commit()
    return stock_list

def add_stock_list(session, company_id, list_id, start_date=None, end_date=None):
    session.add(StockListDatum(company_id=company_id, list_id=list_id, date_added=start_date, date_removed=end_date))

def get_current_stock_list(session, name):
    query1 = session.query(StockList.list_id).filter(StockList.name == name)
    query2 = session.query(StockListDatum.company_id).filter(and_(StockListDatum.list_id == query1, StockListDatum.date_removed == None))
    query = session.query(Company).filter(Company.company_id.in_(query2))

    companies = dict()
    for company in query.all():
        companies[company.symbol] = company
    return companies