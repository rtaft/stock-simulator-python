class StockHolding:
    def __init__(self, company_id=None, symbol=None, quantity=0):
        self.company_id = company_id
        self.quantity = quantity
        self.symbol = symbol
        self.purchase_date = None
        self.cost_basis = 0
        self.sell_date = None
        self.proceeds = 0
        self.current_price = 0

    # TODO add purchase history

class Portfolio:
    def __init__(self):
        self.stock_holdings = []
        self.cash = 0
    
    def get_stock_value(self):
        total = 0
        for stock in self.stock_holdings:
            total += stock.current_price * stock.quantity
        return total
    
    def get_portfolio_value(self):
        return self.cash + self.get_stock_value()
    
    def print_portfolio(self):
        print('\tCash: {:.2f}'.format(self.cash))
        for stock in self.stock_holdings:
            print('\t{}: {:.2f}'.format(stock.symbol, stock.current_price * stock.quantity))