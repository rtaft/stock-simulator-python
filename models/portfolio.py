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
        self.previous_holdings = []
        self.cash = 0
        self.starting_cash = 0
        self.taxes_paid = 0
        self.fees = 0

    def add_cash(self, cash):
        self.cash += cash
        self.starting_cash += cash

    def get_stock_holdings_list(self):
        return list(self.stock_holdings.values())

    def get_stock_holdings(self):
        return self.stock_holdings

    def get_stock_value(self, current_prices):
        total = 0
        for stock in self.stock_holdings.values():
            total += current_prices[stock.company_id] * stock.quantity
        return total
    
    def get_portfolio_value(self, current_prices):
        return self.cash + self.get_stock_value(current_prices)
    
    def print_portfolio(self, current_prices, name=None):
        print ('===========================================================')
        if name:
            print('{}:'.format(name))

        print ("Holdings:")
        for stock in self.stock_holdings.values():
            value = current_prices[stock.company_id] * stock.quantity
            print('\t{}: {}: {:.2f}'.format(stock.symbol, stock.quantity, value))
        
        print ("\nTransactions:")
        for stock in self.previous_holdings:
            total = 0
            for transaction in stock.transactions:
                total += transaction.transaction_price * transaction.transaction_quantity * -1
            print('\t{}\t{:.2f}'.format(stock.symbol, total))

        print('\nResult:')
        print('\tValue: {:.2f}'.format(self.get_stock_value(current_prices)))
        print('\tCash: {:.2f}'.format(self.cash))
        print('\tFees: {:.2f}'.format(self.fees))
        print('\tTotal: {:.2f}'.format(self.get_portfolio_value(current_prices)))
        print ('===========================================================')
    def get_profit(self, current_prices):
        return self.get_portfolio_value(current_prices) - self.starting_cash

    def print_profit(self, current_prices):
        print('Total Profit: {}'.format(self.get_profit(current_prices)))