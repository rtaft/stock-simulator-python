from database.database import Company, Trader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import app_config

def main():
    engine = create_engine('{}://{}:{}@localhost/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    for company in session.query(Company).filter(Company.symbol=='AAPL'):
        print(dict(company.__dict__))

    #trader = Trader()
    #trader.name = 'My DB Test2'
    #trader.location = 'some location'
    #session.add(trader)
    #session.commit()


if __name__ == "__main__":
    main()