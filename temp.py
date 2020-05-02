from database.database import Company, Trader, SplitHistory, StockList, StockListDatum
from sqlalchemy import create_engine, and_, distinct
from sqlalchemy.orm import sessionmaker
import datetime
import app_config
from database.price_history import insert_price_history
from database.simulation import add_simulation,  get_transactions
from database.database import SimulationTrader
from pub.simulation.capital_gains import get_capital_gains
import price_history_manager
import tools
import math 
import pprint


def main():
    engine = create_engine('{}://{}:{}@{}/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_HOST, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    transactions = get_transactions(session, 102)
    cg = get_capital_gains(transactions)
    pprint.pprint(cg)

    # history = price_history_manager.PriceHistoryManager(session=session)
    # history.set_current_date(datetime.date.today())
    # company_id = 13
    # #session.commit()
    # data = tools.bollinger_bands(history, company_id, 30, 30)
    # print(data)



if __name__ == "__main__":
    main()