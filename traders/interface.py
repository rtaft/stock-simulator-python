from models.portfolio import Portfolio

class TraderInterface:
    def __init__(self, simulator, cash=0, portfolio=None):
        self.simulator = simulator
        if portfolio:
            self.portfolio = portfolio
        else:
            self.portfolio = Portfolio()
            self.portfolio.add_cash(cash)

    def setup(self, params=None):
        raise NotImplementedError()

    def get_name(self):
        raise NotImplementedError()

    def process_day(self, current_date, dataset):
        raise NotImplementedError()
    
    def get_portfolio(self):
        return self.portfolio

    def buy(self, symbol, quantity):
        self.simulator.buy(self.portfolio, symbol, quantity)
    
    def sell(self, symbol, quantity):
        self.simulator.sell(self.portfolio, symbol, quantity)
    
    def print_portfolio(self, todays_prices):
        self.portfolio.print_portfolio(todays_prices, self.get_name())
    
    def print_profit(self, todays_prices):
        print ('Profit For {}: {:.2f}'.format(self.get_name(), self.portfolio.get_profit(todays_prices)))
