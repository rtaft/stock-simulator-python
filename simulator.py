import datetime
from time import sleep
import app_config
from database.mysql_db import MySQLDatabase
from models.portfolio import Portfolio, StockHolding, Transaction
from models.company import Company
from traders.test import Test

class Simulator:
    def __init__(self, database):
        self.database = database
        self.price_history = database.get_price_history()
        self.dividend_history = database.get_dividend_history()
        self.current_date = None
        self.datasets = {}

    def setup_datasets(self):
        company_ids = self.database.get_company_ids_in_price_history()
        companies = self.database.get_companies(company_ids=company_ids)
        for exchange in companies:
            for company in companies[exchange].values():
                comp = Company(symbol=company['symbol'], company_id=company['company_id'])
                comp.info = company
                for trade_date, price in self.price_history.get(company['company_id']).items():
                    if trade_date <= self.current_date:
                        comp.price_history[trade_date] = price
                for trade_date, dividend in self.dividend_history.get(company['company_id']).items():
                    if trade_date <= self.current_date:
                        comp.dividend_history[trade_date] = dividend
                self.datasets[company['symbol']] = comp

    def start(self, start_date, end_date, traders):
        self.current_date = start_date
        self.setup_datasets()
        while self.current_date < end_date:
            # TODO validate we are trading today
            self.process_day(traders)
            self.current_date = self.current_date + datetime.timedelta(days=1)
        
       # print("Value: {:.2f}".format(portfolio.get_stock_value()))
       # print("Cash: {:.2f}".format(portfolio.cash))
       # print("Total: {:.2f}".format(portfolio.get_portfolio_value()))

    def process_day(self, traders):
        for company in self.datasets.values():
            price = self.price_history.get(company.company_id, {}).get(self.current_date)
            dividend = self.dividend_history.get(company.company_id, {}).get(self.current_date)
            if price:
                company.price_history[self.current_date] = price
            if dividend:
                company.dividend_history[self.current_date] = dividend
        for trader in traders:
            self.process_day_data(trader.get_portfolio())
            trader.process_day(self.current_date, self.datasets)
        sleep(1)

    def process_day_data(self, portfolio):
        for stock in portfolio.stock_holdings.values():
            if self.current_date in self.price_history[stock.company_id]:
                stock.current_price = self.price_history[stock.company_id][self.current_date]['trade_close']
            dividend = self.dividend_history.get(stock.company_id, {}).get(self.current_date)
            if dividend:
                print("Paying Dividend of {} on {} for {}".format(dividend['dividend'], self.current_date, stock.symbol))
                portfolio.cash += stock.quantity * dividend['dividend']
                # TODO taxes configurable
                # TODO Trade fees configurable
        portfolio.print_portfolio()

    def buy(self, portfolio, symbol, quantity):
        company_id = self.datasets[symbol].company_id
        stock_holding = portfolio.get_stock_holdings().get(symbol)
        current_price = self.price_history[company_id][self.current_date]['trade_close']
        transaction = Transaction(self.current_date, quantity, current_price, 'BUY')
        transaction_cost = current_price * quantity
        if not stock_holding:
            stock_holding = StockHolding(company_id=company_id, symbol=symbol)
            portfolio.stock_holdings[symbol] = stock_holding
        stock_holding.transactions.append(transaction)
        stock_holding.quantity += quantity
        stock_holding.cost_basis += transaction_cost
        portfolio.cash -= transaction_cost
        print('Purchased {} of {} on {} for {:.2f}'.format(quantity, symbol, self.current_date, transaction_cost))
    
    def sell(self, portfolio, symbol, quantity):
        stock_holding = portfolio.get_stock_holdings().get(symbol)
        current_price = self.price_history[stock_holding.company_id][self.current_date]['trade_close']
        transaction = Transaction(self.current_date, -quantity, current_price, 'SELL')
        transaction_value = current_price * quantity
        stock_holding.transactions.append(transaction)
        stock_holding.quantity -= quantity
        portfolio.cash += transaction_value
        print('Sold {} of {} on {} for {:.2f}'.format(quantity, symbol, self.current_date, transaction_value))

def main():
    #cash = float(input("Enter Starting Cash Balance:"))
    #start_date = input("Enter Starting Date:")
    #end_date = input("Enter End Date:")
    start_date = datetime.date(2019, 1, 2)
    end_date = datetime.date(2019, 3, 1)
    database = MySQLDatabase()
    database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
    traders = []
    #TODO load all traders.  Auto vs config?
    simulator = Simulator(database=database)
    traders.append(Test(simulator, 2234.55))
    simulator.start(start_date, end_date, traders)
    

if __name__ == "__main__":
    main()




