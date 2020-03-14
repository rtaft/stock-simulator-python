import datetime
import os
import sys, inspect, importlib
from time import sleep
import time
import memcache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import app_config
from models.portfolio import Portfolio, StockHolding, Transaction
from models.dataset import DataSet
from traders.simple_trader import SimpleTrader
from exceptions import InsuficientFunds, NegativeQuantity

from database.database import Simulation, SimulationTrader
from database.price_history import get_price_history
from database.dividend import get_dividend_history
from database.split import get_split_history
from database.company import get_companies
from database.stock import get_current_stock_list
from database.simulation import add_transaction, add_simulation, add_simulation_trader
from database.trader import get_traders
from traders.interface import TraderInterface
import price_history_manager

class Simulator:
    def __init__(self, session):
        self.session = session
        self.dividend_history = dict()
        self.split_history = dict()
        self.current_date = None
        self.datasets = {}
        self.last_prices = None
        self.todays_prices = None
        self.mem = memcache.Client([(app_config.MEMCACHE_HOST, app_config.MEMCACHE_PORT)])
        self.history = price_history_manager.PriceHistoryManager(session=session)
        self.company_ids = []
    
    def setup_datasets(self):
        #company_ids = get_company_ids_in_price_history(self.session)
        start = time.time()
        companylist = dict()
        companylist = get_current_stock_list(self.session, 'SP500')
        #companylist.update(get_current_stock_list(self.session, 'DOW'))
        self.company_ids=[company.company_id for company in companylist.values()]
        companies = get_companies(self.session,company_ids=self.company_ids)
        #companies = get_companies(self.session)
        self.dividend_history = get_dividend_history(self.session,company_ids=self.company_ids)
        self.split_history = get_split_history(self.session,company_ids=self.company_ids)
        for exchange in companies:
            for company in companies[exchange].values():
                comp = DataSet(company=company, price_history=self.history)
                if company.company_id in self.dividend_history:
                    for trade_date, dividend in self.dividend_history.get(company.company_id).items():
                        if trade_date <= self.current_date:
                            comp.dividend_history[trade_date] = dividend
                if company.company_id in self.split_history:
                    for trade_date, split in self.split_history.get(company.company_id).items():
                        if trade_date <= self.current_date:
                            comp.split_history[trade_date] = split
                self.datasets[company.symbol] = comp
        self.history.initial_load(current_date=self.current_date)
        print('Data Load Took {:.0f}s'.format(time.time()-start))

    def start(self, start_date, end_date, sim_traders, simulation_id):
        """
            :param sim_traders: dict of simulation_traders to traders
        """
        self.current_date = start_date
        self.mem.set('progress_{}'.format(simulation_id), 'Loading...')
        self.setup_datasets()
        while self.current_date < end_date:
            self.history.set_current_date(self.current_date)
            self.mem.set('progress_{}'.format(simulation_id), self.current_date)
            if app_config.DEBUG:
                print ('Process Day {}'.format(self.current_date))
            self.todays_prices = self.get_day_prices()
            if self.todays_prices:
                self.last_prices = self.todays_prices
                self.process_day(sim_traders)
            self.current_date = self.current_date + datetime.timedelta(days=1)
        self.mem.set('progress_{}'.format(simulation_id), 'Completed.')
        for sim_trader, trader in sim_traders.items():
            trader.print_portfolio(self.last_prices)
            trader.print_profit(self.last_prices)
            sim_trader.ending_value = trader.portfolio.get_portfolio_value(self.last_prices)
        self.session.commit()


    def process_day(self, sim_traders):
        """
            :param sim_traders: dict of simulation_traders to traders
        """
        for dataset in self.datasets.values():
            dividend = self.dividend_history.get(dataset.company.company_id, {}).get(self.current_date)
            split = self.split_history.get(dataset.company.company_id, {}).get(self.current_date)

            if dividend:
                dataset.dividend_history[self.current_date] = dividend
            if split:
                dataset.split_history[self.current_date] = split
        for sim_trader, trader in sim_traders.items():
            self.process_day_data(trader.get_portfolio())
            trader.process_day(self.current_date, self.datasets, sim_trader.simulation_trader_id)
            if app_config.DEBUG:
                trader.print_portfolio(self.todays_prices)

        #sleep(1)

    def process_day_data(self, portfolio):
        for stock in portfolio.stock_holdings.values():
            current_price_history = self.history.get_current_price(stock.company_id)
            if current_price_history:
                stock.current_price = current_price_history.trade_close
            dividend = self.dividend_history.get(stock.company_id, {}).get(self.current_date)
            if dividend:
                if app_config.DEBUG:
                    print("Paying Dividend of {} on {} for {}".format(dividend.dividend, self.current_date, stock.symbol))
                payout = stock.quantity * dividend.dividend
                portfolio.cash += payout
                portfolio.cash -= payout * app_config.QUALIFIED_TAX_RATE
                portfolio.taxes_paid += payout * app_config.QUALIFIED_TAX_RATE
            split = self.split_history.get(stock.company_id, {}).get(self.current_date)
            if split:
                if not app_config.DEBUG:
                    print("Processing split of {} on {} for {}".format(split.ratio, self.current_date, stock.symbol))
                stock.quantity *= split.ratio

    def get_day_prices(self):
        try:
            prices = dict()
            days_prices = self.history.get_days_prices(company_ids=self.company_ids)
            for dataset in self.datasets.values():
                price = days_prices.get(dataset.company.company_id, {}).get(self.current_date)
                if price:
                    prices[dataset.company.company_id] = price.trade_close
            return prices
        except:
            import traceback
            traceback.print_exc()

    def buy(self, trader, symbol, quantity, sim_trader_id):
        if quantity <= 0:
            raise NegativeQuantity('Quantity is negative {}'.format(quantity))
        company_id = self.datasets[symbol].company.company_id
        stock_holding = trader.portfolio.get_stock_holdings().get(symbol)
        current_price = self.history.get_current_price(company_id).trade_close
        transaction = Transaction(sim_trader_id, self.current_date, quantity, current_price, 'BUY', symbol)
        transaction_cost = current_price * quantity + app_config.TRADE_FEES
        trader.portfolio.fees += app_config.TRADE_FEES

        if transaction_cost > trader.portfolio.cash:
            raise InsuficientFunds('Insuficient Funds {} > {}'.format(transaction_cost, trader.portfolio.cash))

        if not stock_holding:
            stock_holding = StockHolding(company_id=company_id, symbol=symbol)
            trader.portfolio.stock_holdings[symbol] = stock_holding
        stock_holding.transactions.append(transaction)
        add_transaction(self.session, sim_trader_id, transaction.transaction_date, transaction.transaction_quantity, transaction.transaction_price, transaction.transaction_type, symbol)
        stock_holding.quantity += quantity
        stock_holding.cost_basis += transaction_cost
        trader.portfolio.cash -= transaction_cost
        print('Purchased {} of {} on {} for {:.2f}'.format(quantity, symbol, self.current_date, transaction_cost))
    
    def sell(self, trader, symbol, quantity, sim_trader_id):
        company_id = self.datasets[symbol].company.company_id
        stock_holding = trader.portfolio.get_stock_holdings().get(symbol)
        current_price = self.history.get_current_price(company_id).trade_close
        transaction = Transaction(sim_trader_id, self.current_date, -quantity, current_price, 'SELL', symbol)
        transaction_value = current_price * quantity - app_config.TRADE_FEES
        trader.portfolio.fees += app_config.TRADE_FEES
        stock_holding.transactions.append(transaction)
        add_transaction(self.session, sim_trader_id, transaction.transaction_date, transaction.transaction_quantity, transaction.transaction_price, transaction.transaction_type, symbol)
        stock_holding.quantity -= quantity
        trader.portfolio.cash += transaction_value
        # TODO how to handle short term taxes
        trader.portfolio.taxes_paid += transaction_value * app_config.QUALIFIED_TAX_RATE
        trader.portfolio.cash -= transaction_value * app_config.QUALIFIED_TAX_RATE
        if stock_holding.quantity == 0:
            trader.portfolio.previous_holdings.append(stock_holding)
            del trader.portfolio.stock_holdings[symbol]
        print('Sold {} of {} on {} for {:.2f}'.format(quantity, symbol, self.current_date, transaction_value))

    def initiate_traders(self, trader_data, starting_cash=0):
        """
            :param trader_data: Dictionary of trader_ids to trader data params
        """
        traders = get_traders(self.session, trader_ids=trader_data.keys()) #TODO multiple traders support
        trader_instances = []
        for trader in traders:
            if trader.location[:7] == 'file://':
                path = 'traders.{}'.format(trader.location[7:-3])
                importlib.import_module(path)
                trader_module = self.get_class(path)
                for name, obj in inspect.getmembers(trader_module):
                    if inspect.isclass(obj):
                        if obj != TraderInterface:
                            for mro in inspect.getmro(obj):
                                if mro == TraderInterface:
                                    print('Adding {}'.format(name))
                                    trader = obj(self, trader_id=trader.trader_id, cash=trader_data[trader.trader_id].get('starting_cash', starting_cash))
                                    trader.setup(trader_data[trader.trader_id])
                                    trader_instances.append(trader)
        return trader_instances

    def get_class(self, kls ):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

def main():
    # TODO starting values configurable
    #cash = float(input("Enter Starting Cash Balance:"))
    #start_date = input("Enter Starting Date:")
    #end_date = input("Enter End Date:")
    start = time.time()
    start_date = datetime.date(2016, 1, 1)
    end_date = datetime.date(2017, 1, 1)
    starting_balance = 60000
    engine = create_engine('{}://{}:{}@{}/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_HOST, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    #TODO load all traders.  Auto vs config?
    simulator = Simulator(session=session)
    traders = simulator.initiate_traders(
        #{1: dict(starting_cash=starting_balance, max_holding=30, loss_sell_ratio=0.5, gain_sell_ratio=2.0, minimum_transaction=2000),
         {2: dict(starting_cash=10000)})

    simulation = add_simulation(session, start_date, end_date, starting_balance, datetime.datetime.now(), 'Temp Description')
    sim_traders = dict()
    session.commit()
    for trader in traders:
        sim_trader = add_simulation_trader(session, simulation.simulation_id, trader.trader_id)
        session.commit()
        sim_traders[sim_trader] = trader
    simulator.start(start_date, end_date, sim_traders, simulation.simulation_id)
    
    session.commit()
    session.close()
    print('Simulation Took {:.0f}s'.format(time.time()-start))
    print()

if __name__ == "__main__":
    main()




