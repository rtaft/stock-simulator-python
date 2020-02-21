from sqlalchemy import between, and_, distinct
from database.database import SplitHistory

def remove_split_history(session, company_id):
    return session.query(SplitHistory).filter(SplitHistory.company_id == company_id).delete()

def insert_splits_bulk(session, split_history_list):
    #session.add_all(split_history_list)
    session.execute(SplitHistory.__table__.insert(), split_history_list)


def insert_split(session, company_id, split_date, ratio):
    session.add(SplitHistory(company_id=company_id, split_date=split_date, ratio=ratio))

def get_split_history(session, company_ids=None, start_date=None, end_date=None):
    where = []
    if company_ids:
        where.append(SplitHistory.company_id.in_(company_ids))
    elif start_date and end_date:
        where.append(between(SplitHistory.split_date, start_date, end_date))

    query = session.query(SplitHistory)
    if where:
        query = query.filter(and_(*where))
    full_history = dict()
    for split_history in query.all():
        company = full_history.setdefault(split_history.company_id, dict())
        if not split_history.split_date:
            print('Empty Split date {}'.format(split_history))
        elif split_history.split_date not in company:
            company[split_history.split_date] = split_history
        else:
            print('Duplicate Split found for {} {}'.format(split_history.company_id, split_history.split_date))
    return full_history
