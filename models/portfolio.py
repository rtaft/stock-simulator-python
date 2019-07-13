class StockHolding:
    def __init__(self, company_id=None, symbol=None, quantity=0):
        self.company_id = company_id
        self.symbol = symbol
        self.quantity = quantity
        self.cost_basis = 0.0
        self.transactions = []

class Transaction:
    def __init__(self, transaction_date, transaction_quantity, transaction_price, transaction_type):
        self.transaction_quantity = transaction_quantity
        self.transaction_date = transaction_date
        self.transaction_price = transaction_price
        self.transaction_type = transaction_type

class Portfolio:
    def __init__(self):
        self.stock_holdings = dict()
        self.cash = 0
    
    def get_stock_holdings_list(self):
        return list(self.stock_holdings.values())

    def get_stock_holdings(self):
        return self.stock_holdings

    def get_stock_value(self):
        total = 0
        for stock in self.stock_holdings.values():
            total += stock.current_price * stock.quantity
        return total
    
    def get_portfolio_value(self):
        return self.cash + self.get_stock_value()
    
    def print_portfolio(self): #TODO add current value to print
        print('\tCash: {:.2f}'.format(self.cash))
        for stock in self.stock_holdings.values():
            print('\t{}: {}'.format(stock.symbol, stock.quantity))