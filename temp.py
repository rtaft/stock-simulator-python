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
import json
import os
import random
import shutil
from traders.simple_trader import SimpleTraderSchema
from marshmallow_jsonschema import JSONSchema
from traders import util

def main():
    # engine = create_engine('{}://{}:{}@{}/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_HOST, app_config.DB_NAME))
    # engine.connect()
    # Session = sessionmaker(bind=engine)
    # session = Session()
    import git
    temp = 'tmp'
    pathname = '{}/repo{}'.format(temp, random.randint(100000, 1000000))
    if not os.path.exists(temp):
        os.mkdir(temp)
    os.mkdir(pathname)
    print("Download to {}".format(pathname))
    git.Git(pathname).clone("git@github.com:rtaft/my-stock-traders.git")
    #files = os.listdir(pathname)
    trader_files = []
    existing_files = []

    #for pathname in files:
    for root, dirs, files in os.walk(pathname, topdown=False):
        for filename in files:
            if filename[-3:] == '.py':
                fullpath = os.path.join(root, filename)
                print(fullpath)
                print(util.is_trader_instance(fullpath[:-3].replace('/', '.')))
                #trader_files.append(filename)
    

    shutil.rmtree(pathname)



if __name__ == "__main__":
    main()
  