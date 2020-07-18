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
from database.company import get_companies, get_companies_by_id
from database.stock import get_current_stock_list
from database.simulation import add_transaction, add_simulation, add_simulation_trader
from database.trader import get_traders_by_id
from traders.interface import TraderInterface
from traders.util import initiate_traders
import price_history_manager

class Simulator:
    def __init__(self, session, stock_list_name='All'):
        self.session = session
        self.dividend_history = dict()
        self.split_history = dict()
        self.current_date = None
        self.datasets = {}
        self.last_prices = None
        self.todays_prices = None
        self.stock_list_name = stock_list_name
        self.mem = memcache.Client([(app_config.MEMCACHE_HOST, app_config.MEMCACHE_PORT)])
        self.history = None
        self.company_ids = []

    def setup_datasets(self):
        start = time.time()
        if self.stock_list_name == 'All':
            companies = get_companies_by_id(self.session)
            self.company_ids = companies.keys()
        else:
            companylist = get_current_stock_list(self.session, self.stock_list_name)
            self.company_ids=[company.company_id for company in companylist.values()]
            companies = get_companies_by_id(self.session,company_ids=self.company_ids)

        self.history = price_history_manager.PriceHistoryManager(session=self.session, company_ids=self.company_ids)
        self.dividend_history = get_dividend_history(self.session,company_ids=self.company_ids)
        self.split_history = get_split_history(self.session,company_ids=self.company_ids)
        for company in companies.values():
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

    def start(self, start_date, end_date, sim_traders, simulation_id, callback=None):
        """
            :param sim_traders: dict of simulation_traders to traders
        """
        self.current_date = start_date
        self.mem.set('progress_{}'.format(simulation_id), 'Loading...')
        if callback:
            callback(simulation_id, 'Loading...')
        self.setup_datasets()
        while self.current_date < end_date:
            self.history.set_current_date(self.current_date)
            self.mem.set('progress_{}'.format(simulation_id), self.current_date)
            if callback:
                callback(simulation_id, self.current_date)
            if app_config.DEBUG >= 2:
                print ('Process Day {}'.format(self.current_date))
            self.todays_prices = self.get_day_prices()
            if self.todays_prices:
                self.last_prices = self.todays_prices
                self.process_day(sim_traders)
            self.current_date = self.current_date + datetime.timedelta(days=1)
        for sim_trader, trader in sim_traders.items():
            self.sell_all(trader, sim_trader.simulation_trader_id)
            trader.print_portfolio(self.last_prices)
            trader.print_profit(self.last_prices)
            sim_trader.ending_value = trader.portfolio.get_portfolio_value(self.last_prices)
        if callback:
            callback(simulation_id, 'Completed.')
        self.mem.set('progress_{}'.format(simulation_id), 'Completed.')
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
            self.process_day_data(trader.get_portfolio(), sim_trader.simulation_trader_id)
            trader.process_day(self.current_date, self.datasets, sim_trader.simulation_trader_id)
            if app_config.DEBUG >= 2:
                trader.print_portfolio(self.todays_prices)

        #sleep(1)

    def process_day_data(self, portfolio, sim_trader_id):
        for stock in portfolio.stock_holdings.values():
            current_price_history = self.history.get_current_price(stock.company_id)
            if current_price_history:
                stock.current_price = current_price_history.trade_close
            dividend = self.dividend_history.get(stock.company_id, {}).get(self.current_date)
            if dividend:
                taxes = round(stock.quantity * dividend.dividend * app_config.DIVIDEND_TAX_RATE, 2)
                payout = round(stock.quantity * dividend.dividend - taxes, 2)
                add_transaction(self.session, sim_trader_id, self.current_date, stock.quantity, dividend.dividend, taxes, 'DIV', payout, stock.company_id)
                portfolio.cash += payout
                portfolio.taxes_paid += taxes
                if app_config.DEBUG:
                    print("Paying Dividend of {} on {} for {}  Balance: {:.2f}".format(dividend.dividend, self.current_date, stock.symbol, portfolio.cash))
            split = self.split_history.get(stock.company_id, {}).get(self.current_date)
            if split:
                if not app_config.DEBUG:
                    print("Processing split of {} on {} for {}".format(split.ratio, self.current_date, stock.symbol))
                stock.quantity *= split.ratio
                if stock.quantity != round(stock.quantity):
                    leftover = stock.quantity - stock.quantity//1
                    stock.quantity = stock.quantity//1
                    if leftover:

                        taxes = round(stock.current_price * leftover * app_config.DIVIDEND_TAX_RATE, 2)
                        payout = round(stock.current_price * leftover - taxes, 2)
                        add_transaction(self.session, sim_trader_id, self.current_date, stock.quantity, leftover, taxes, 'DIV', payout, stock.company_id)
                        portfolio.cash += payout
                        portfolio.taxes_paid += taxes
                        if app_config.DEBUG:
                            print("Paying Split Dividend of {} on {} for {}  Balance: {:.2f}".format(leftover, self.current_date, stock.symbol, portfolio.cash))

                add_transaction(self.session, sim_trader_id, self.current_date, split.ratio, 0, 0, 'SPLIT', 0, stock.company_id)

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
        transaction_cost = current_price * quantity + app_config.TRADE_FEES
        trader.portfolio.fees += app_config.TRADE_FEES

        if transaction_cost > trader.portfolio.cash:
            raise InsuficientFunds('Insuficient Funds {} > {}'.format(transaction_cost, trader.portfolio.cash))

        if not stock_holding:
            stock_holding = StockHolding(company_id=company_id, symbol=symbol)
            trader.portfolio.stock_holdings[symbol] = stock_holding

        transaction = add_transaction(self.session, sim_trader_id, self.current_date, quantity, current_price, 0, 'BUY', -transaction_cost, company_id)
        stock_holding.transactions.append(transaction)
        stock_holding.quantity += quantity
        stock_holding.cost_basis += transaction_cost
        trader.portfolio.cash -= transaction_cost
        print('Purchased {} of {} on {} for {:.2f}  Balance: {:.2f}'.format(quantity, symbol, self.current_date, transaction_cost, trader.portfolio.cash))

    def sell(self, trader, symbol, quantity, sim_trader_id):
        company_id = self.datasets[symbol].company.company_id
        stock_holding = trader.portfolio.get_stock_holdings().get(symbol)
        if stock_holding.quantity < quantity:
            raise Exception("Cannot sell {} shares of {}, there are only {} in the portfolio.".format(quantity, symbol, stock_holding.quantity))
        current_price = self.history.get_current_price(company_id).trade_close
        transaction_value = current_price * quantity - app_config.TRADE_FEES
        trader.portfolio.fees += app_config.TRADE_FEES
        tax = 0 #round(transaction_value * app_config.QUALIFIED_TAX_RATE, 2)
        transaction = add_transaction(self.session, sim_trader_id, self.current_date, -quantity, current_price, tax, 'SELL', transaction_value, company_id)
        stock_holding.transactions.append(transaction)
        stock_holding.quantity -= quantity
        trader.portfolio.cash += transaction_value
        # TODO how to handle short term taxes
        trader.portfolio.taxes_paid += tax
        trader.portfolio.cash -= tax
        if stock_holding.quantity == 0:
            trader.portfolio.previous_holdings.append(stock_holding)
            del trader.portfolio.stock_holdings[symbol]
        print('Sold {} of {} on {} for {:.2f}  Balance: {:.2f}'.format(quantity, symbol, self.current_date, transaction_value, trader.portfolio.cash))

    def sell_all(self, trader, sim_trader_id):
        data = dict()
        data.update(trader.portfolio.get_stock_holdings())
        for symbol, stock in data.items():
            self.sell(trader, symbol, stock.quantity, sim_trader_id)

    def create_traders(self, trader_data):
        """
            :param trader_data: Dictionary of trader_ids to trader data params
        """
        traders_by_id = get_traders_by_id(self.session, trader_ids=[trader['trader_id']['value'] for trader in trader_data])
        traders = []
        for trader in trader_data:
            traders.append(traders_by_id[int(trader['trader_id']['value'])])
        trader_instances = initiate_traders(self, traders)
        for i in range(len(trader_instances)):
            trader = trader_instances[i]
            print('Setup {}'.format(trader.get_name()))
            data = dict()
            for key, value in trader_data[i].items():
                data[key] = value.get('value')
            trader.setup(data)
        return trader_instances

def main():
    # TODO starting values configurable
    #cash = float(input("Enter Starting Cash Balance:"))
    #start_date = input("Enter Starting Date:")
    #end_date = input("Enter End Date:")
    start = time.time()
    start_date = datetime.date(2007, 1, 1)
    end_date = datetime.date(2010, 1, 1)
    starting_balance = 60000
    stock_list = 'SP500'
    engine = create_engine('{}://{}:{}@{}/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_HOST, app_config.DB_NAME))
    engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    #TODO load all traders.  Auto vs config?
    simulator = Simulator(session=session, stock_list_name=stock_list)
    traders = simulator.create_traders(
         {1: dict(starting_cash=starting_balance, max_holding=30, loss_sell_ratio=0.5, gain_sell_ratio=2.0, minimum_transaction=2000),
          2: dict(starting_cash=starting_balance)})

    simulation = add_simulation(session, start_date, end_date, datetime.datetime.now(), 'Temp Description', stock_list)
    sim_traders = dict()
    session.commit()
    for trader in traders:
        sim_trader = add_simulation_trader(session, simulation.simulation_id, trader.trader_id, starting_balance)
        session.commit()
        sim_traders[sim_trader] = trader
    simulator.start(start_date, end_date, sim_traders, simulation.simulation_id)

    session.commit()
    session.close()
    print('Simulation Took {:.0f}s'.format(time.time()-start))
    print()

if __name__ == "__main__":
    main()




