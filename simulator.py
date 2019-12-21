import datetime
from time import sleep
import time
import app_config
from database.mysql_db import MySQLDatabase
from models.portfolio import Portfolio, StockHolding, Transaction
from models.company import Company
from models.simulation import Simulation
from traders.simple_trader import SimpleTrader
from exceptions import InsuficientFunds, NegativeQuantity

class Simulator:
    def __init__(self, database):
        self.database = database
        self.price_history = dict()
        self.dividend_history = dict()
        self.split_history = dict()
        self.current_date = None
        self.datasets = {}
        self.last_prices = None
        self.todays_prices = None

    def setup_datasets(self):
        #company_ids = self.database.get_company_ids_in_price_history()
        start = time.time()
        companylist = self.database.get_current_stock_list('SP500')
        companylist.update(self.database.get_current_stock_list('DOW'))
        company_ids=[company['company_id'] for company in companylist.values()]
        companies = self.database.get_companies(company_ids=company_ids)
        self.price_history = self.database.get_price_history(company_ids=company_ids)
        self.dividend_history = self.database.get_dividend_history(company_ids=company_ids)
        self.split_history = self.database.get_split_history(company_ids=company_ids)
        for exchange in companies:
            for company in companies[exchange].values():
                comp = Company(symbol=company['symbol'], company_id=company['company_id'])
                comp.info = company
                if company['company_id'] in self.price_history:
                    for trade_date, price in self.price_history.get(company['company_id']).items():
                        if trade_date <= self.current_date:
                            comp.price_history[trade_date] = price
                else:
                    print('Could not find price history for {}'.format(company['symbol']))
                    continue
                if company['company_id'] in self.dividend_history:
                    for trade_date, dividend in self.dividend_history.get(company['company_id']).items():
                        if trade_date <= self.current_date:
                            comp.dividend_history[trade_date] = dividend
                if company['company_id'] in self.split_history:
                    for trade_date, split in self.split_history.get(company['company_id']).items():
                        if trade_date <= self.current_date:
                            comp.split_history[trade_date] = split
                self.datasets[company['symbol']] = comp
        print('Data Load Took {:.0f}s'.format(time.time()-start))

    def start(self, start_date, end_date, traders):
        self.current_date = start_date
        self.setup_datasets()
        while self.current_date < end_date:
            if app_config.DEBUG:
                print ('Process Day {}'.format(self.current_date))
            self.todays_prices = self.get_day_prices()
            if self.todays_prices:
                self.last_prices = self.todays_prices
                self.process_day(traders)
            self.current_date = self.current_date + datetime.timedelta(days=1)
        for trader in traders:
            trader.print_portfolio(self.last_prices)
            trader.print_profit(self.last_prices)

    def process_day(self, traders):
        for company in self.datasets.values():
            price = self.price_history.get(company.company_id, {}).get(self.current_date)
            dividend = self.dividend_history.get(company.company_id, {}).get(self.current_date)
            split = self.split_history.get(company.company_id, {}).get(self.current_date)

            if price:
                company.price_history[self.current_date] = price
            if dividend:
                company.dividend_history[self.current_date] = dividend
            if split:
                company.split_history[self.current_date] = split
        for trader in traders:
            self.process_day_data(trader.get_portfolio())
            trader.process_day(self.current_date, self.datasets)
            if app_config.DEBUG:
                trader.print_portfolio(self.todays_prices)
        #sleep(1)

    def process_day_data(self, portfolio):
        for stock in portfolio.stock_holdings.values():
            if self.current_date in self.price_history[stock.company_id]:
                stock.current_price = self.price_history[stock.company_id][self.current_date]['trade_close']
            dividend = self.dividend_history.get(stock.company_id, {}).get(self.current_date)
            if dividend:
                if app_config.DEBUG:
                    print("Paying Dividend of {} on {} for {}".format(dividend['dividend'], self.current_date, stock.symbol))
                payout = stock.quantity * dividend['dividend']
                portfolio.cash += payout
                portfolio.cash -= payout * app_config.QUALIFIED_TAX_RATE
                portfolio.taxes_paid += payout * app_config.QUALIFIED_TAX_RATE
            split = self.split_history.get(stock.company_id, {}).get(self.current_date)
            if split:
                if not app_config.DEBUG:
                    print("Processing split of {} on {} for {}".format(split['ratio'], self.current_date, stock.symbol))
                stock.quantity *= split['ratio']

    def get_day_prices(self):
        prices = dict()
        for company in self.datasets.values():
            price = self.price_history.get(company.company_id, {}).get(self.current_date)
            if price:
                prices[company.company_id] = price['trade_close']
        return prices

    def buy(self, trader, symbol, quantity):
        if quantity <= 0:
            raise NegativeQuantity('Quantity is negative {}'.format(quantity))
        company_id = self.datasets[symbol].company_id
        stock_holding = trader.portfolio.get_stock_holdings().get(symbol)
        current_price = self.price_history[company_id][self.current_date]['trade_close']
        transaction = Transaction(trader.simulation.simulation_id, self.current_date, quantity, current_price, 'BUY', symbol)
        transaction_cost = current_price * quantity + app_config.TRADE_FEES
        trader.portfolio.fees += app_config.TRADE_FEES

        if transaction_cost > trader.portfolio.cash:
            raise InsuficientFunds('Insuficient Funds {} > {}'.format(transaction_cost, trader.portfolio.cash))

        if not stock_holding:
            stock_holding = StockHolding(company_id=company_id, symbol=symbol)
            trader.portfolio.stock_holdings[symbol] = stock_holding
        stock_holding.transactions.append(transaction)
        self.database.add_transaction(transaction.simulation_id, transaction.transaction_date, transaction.transaction_quantity, transaction.transaction_price, transaction.transaction_type, symbol)
        stock_holding.quantity += quantity
        stock_holding.cost_basis += transaction_cost
        trader.portfolio.cash -= transaction_cost
        print('Purchased {} of {} on {} for {:.2f}'.format(quantity, symbol, self.current_date, transaction_cost))
    
    def sell(self, trader, symbol, quantity):
        stock_holding = trader.portfolio.get_stock_holdings().get(symbol)
        current_price = self.price_history[stock_holding.company_id][self.current_date]['trade_close']
        transaction = Transaction(trader.simulation.simulation_id, self.current_date, -quantity, current_price, 'SELL', symbol)
        transaction_value = current_price * quantity - app_config.TRADE_FEES
        trader.portfolio.fees += app_config.TRADE_FEES
        stock_holding.transactions.append(transaction)
        self.database.add_transaction(transaction.simulation_id, transaction.transaction_date, transaction.transaction_quantity, transaction.transaction_price, transaction.transaction_type, symbol)
        stock_holding.quantity -= quantity
        trader.portfolio.cash += transaction_value
        # TODO how to handle short term taxes
        trader.portfolio.taxes_paid += transaction_value * app_config.QUALIFIED_TAX_RATE
        trader.portfolio.cash -= transaction_value * app_config.QUALIFIED_TAX_RATE
        if stock_holding.quantity == 0:
            trader.portfolio.previous_holdings.append(stock_holding)
            del trader.portfolio.stock_holdings[symbol]
        print('Sold {} of {} on {} for {:.2f}'.format(quantity, symbol, self.current_date, transaction_value))

def main():
    # TODO starting values configurable
    #cash = float(input("Enter Starting Cash Balance:"))
    #start_date = input("Enter Starting Date:")
    #end_date = input("Enter End Date:")
    start_date = datetime.date(2016, 1, 1)
    end_date = datetime.date(2017, 1, 1)
    starting_balance = 60000
    database = MySQLDatabase()
    database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
    traders = []
    #TODO load all traders.  Auto vs config?
    simulator = Simulator(database=database)
    simple_trader = SimpleTrader(simulator, starting_balance)
    simple_trader.setup(params=dict(max_holding=30, loss_sell_ratio=0.5, gain_sell_ratio=2.0, minimum_transaction=2000))
    simulation = Simulation(1, start_date, end_date, starting_balance, datetime.datetime.now(), None, 'Temp Description')
    simple_trader.simulation = simulation
    simulation.simulation_id = database.add_simulation(start_date, end_date, starting_balance, datetime.datetime.now(), None, 'Temp Description')
    traders.append(simple_trader)
    simulator.start(start_date, end_date, traders)
    database.commit()

if __name__ == "__main__":
    main()




