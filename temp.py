from database.database import Company, Trader, SplitHistory, PriceHistory, StockList, StockListDatum
from sqlalchemy import create_engine, and_, distinct
from sqlalchemy.orm import sessionmaker
import datetime
import app_config
from database.price_history import insert_price_history
from database.simulation import add_simulation
from database.database import SimulationTrader

def main():
    engine = create_engine('{}://{}:{}@localhost/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    name = 'DOW'
    start_date = datetime.date(2016, 1, 1)
    end_date = datetime.date(2017, 1, 1)
    starting_balance = 60000

    simulation = add_simulation(session, start_date, end_date, starting_balance, datetime.datetime.now(), 'Temp Description')
    sim_trader = SimulationTrader(trader_id=4)
    sim_trader2 = SimulationTrader(trader_id=3)
    simulation.simulation_traders = [sim_trader, sim_trader2]
    session.commit()


    #query = session.query(Company).filter(Company.company_id.in_(session.query(StockListDatum.company_id).filter(and_(StockListDatum.list_id == session.query(StockList.list_id).filter(StockList.name == name), StockListDatum.date_removed == None))))
    #query1 = session.query(StockList.list_id).filter(StockList.name == name)
    #query2 = session.query(StockListDatum.company_id).filter(and_(StockListDatum.list_id == query1, StockListDatum.date_removed == None))
    #query = session.query(Company).filter(Company.company_id.in_(query2))
    #for company in query.all():
    #    print(company.__dict__)
    #print(session.query(distinct(PriceHistory.company_id)).all())
    #print([xx[0] for xx in session.query(PriceHistory.company_id).distinct().all()])
    #query = session.query(PriceHistory).filter(PriceHistory.history_id == 24200863).delete()
    #print(query)
    #session.commit()
    #insert_price_history(session, company_id=9881, trade_date=)
    #session.rollback()
    #query = session.query(Company, SplitHistory).filter(Company.symbol=='AAPL' and Company.company_id == SplitHistory.company_id)
    #query = session.query(Company).join(SplitHistory, and_(Company.company_id == SplitHistory.company_id, Company.symbol=='AAPL')).filter(Company.symbol=='AAPL')
    #print(query)
    #for company, split in query.all():
    #    print(dict(company.__dict__))
    #    print(dict(split.__dict__))
    #trader = Trader()
    #trader.name = 'My DB Test2'
    #trader.location = 'some location'
    #session.add(trader)
    #session.commit()


if __name__ == "__main__":
    main()