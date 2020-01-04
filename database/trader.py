from sqlalchemy import between, and_, distinct
from database.database import Trader

def get_traders(session, trader_ids=None):
    query = session.query(Trader)

    if trader_ids:
        query = query.filter(Trader.trader_id.in_(trader_ids))
    
    traders = []
    for trader in Trader:
        traders.append(trader)
    return traders

def add_trader(session, name, location):
    trader = Trader(name=name, location=location)
    session.add(trader)
    return trader

def delete_trader(session, trader_id):
    return session.query(Trader).filter(Trader.trader_id == trader_id).delete()
