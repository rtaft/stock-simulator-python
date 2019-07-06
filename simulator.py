import datetime
from time import sleep
import app_config
from database.mysql_db import MySQLDatabase
from models.stock import Portfolio, StockHolding


class Simulator:
    def __init__(self, database, price_history=None, dividend_history=None):
        self.database = database
        self.price_history = price_history
        self.dividend_history = dividend_history

    def start(self, start_date, end_date, portfolio):
        if not self.price_history:
            self.price_history = self.database.get_price_history_by_date(start_date, end_date)
        if not self.dividend_history:
            self.dividend_history = self.database.get_dividend_history_by_date(start_date, end_date)
        current_date = start_date
        while current_date < end_date:
            print(current_date)
            self.process_day(current_date, portfolio)
            current_date = current_date + datetime.timedelta(days=1)
        
        # TODO process dividends - ex dividend date vs date of record

        print("Value: {:.2f}".format(portfolio.get_stock_value()))
        print("Cash: {:.2f}".format(portfolio.cash))
        print("Total: {:.2f}".format(portfolio.get_portfolio_value()))

    def process_day(self, process_date, portfolio):
        for stock in portfolio.stock_holdings:
            if process_date in self.price_history[stock.company_id]:
                stock.current_price = self.price_history[stock.company_id][process_date]['trade_close']
        portfolio.print_portfolio()
        sleep(1)
    
    def purchase(self, portfolio, company, trade_date, quantity):
        stock = StockHolding(company_id=company['company_id'], symbol=company['symbol'], quantity=quantity)
        stock.cost_basis = self.price_history[stock.company_id][trade_date]['trade_close'] * quantity
        stock.current_price = self.price_history[stock.company_id][trade_date]['trade_close']
        stock.purchase_date = trade_date
        portfolio.cash -= stock.cost_basis
        portfolio.stock_holdings.append(stock)

def main():
    #cash = float(input("Enter Starting Cash Balance:"))
    #start_date = input("Enter Starting Date:")
    #end_date = input("Enter End Date:")
    cash = 10000
    start_date = datetime.date(2019, 1, 2)
    end_date = datetime.date(2019, 2, 1)
    database = MySQLDatabase()
    database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
    price_history = database.get_price_history_by_date(start_date, end_date)
    dividend_history = database.get_dividend_history_by_date(start_date, end_date)
    portfolio = Portfolio()
    portfolio.cash = 2234.55
   
    simulator = Simulator(database=database, price_history=price_history, dividend_history=dividend_history)
    simulator.purchase(portfolio, dict(company_id=9786, symbol='AAPL'), datetime.date(2019, 1, 2), 10)
    simulator.start(start_date, end_date, portfolio)
    

if __name__ == "__main__":
    main()




