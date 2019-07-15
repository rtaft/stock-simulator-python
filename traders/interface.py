from models.portfolio import Portfolio

class TraderInterface:
    def __init__(self, simulation, cash=0, portfolio=None):
        self.simulation = simulation
        if portfolio:
            self.portfolio = portfolio
        else:
            self.portfolio = Portfolio()
            self.portfolio.cash = cash

    def setup(self):
        raise NotImplementedError()

    def process_day(self, current_date, dataset):
        raise NotImplementedError()
    
    def get_portfolio(self):
        return self.portfolio

    def buy(self, symbol, quantity):
        self.simulation.buy(self.portfolio, symbol, quantity)
    
    def sell(self, symbol, quantity):
        self.simulation.sell(self.portfolio, symbol, quantity)
    