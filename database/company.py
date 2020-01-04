from sqlalchemy import between, and_, distinct
from database.database import Company

def add_company_info(session, company_name, symbol, exchange, ipo, sector, industry):
    company = Company(company_name=company_name, symbol=symbol, exchange=exchange, ipo=ipo, sector=sector, industry=industry)
    session.add(company)
    return company

def get_companies(session, company_ids=None):
    query = session.query(Company)
    if company_ids:
        query = query.filter(Company.company_id.in_(company_ids))
    companies = dict()

    for company in query.all():
        companies.setdefault(company.exchange, dict())[company.symbol] = company

    return companies

def get_companies_by_id(session, company_ids=None):
    query = session.query(Company)
    if company_ids:
        query = query.filter(Company.company_id.in_(company_ids))
    companies = dict()

    for company in query.all():
        companies[company.company_id] = company

    return companies

def find_company_by_symbol(session, symbol=None):
    companies = []
    query = session.query(Company)
    if symbol:
        query = query.filter(Company.symbol == symbol)
    for company in query.all():
        companies.append(company)
    return companies