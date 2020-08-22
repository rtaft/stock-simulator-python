from marshmallow import Schema, fields, validate, EXCLUDE

from models.portfolio import Portfolio

class TraderSchema(Schema):
    starting_balance = fields.Integer(required=True, metadata=dict(fieldname="Starting Balance", value=10000, notes="Starting cash balance to trade with."))
    description = fields.String(required=False, allow_none=True, metadata=dict(fieldname="Description", notes="Short description of trader."))

class TraderInterface:
    def __init__(self, simulator, trader_id=None, cash=0, portfolio=None):
        self.simulator = simulator
        self.trader_id = trader_id
        self.description = ''
        if portfolio:
            self.portfolio = portfolio
        else:
            self.portfolio = Portfolio()
            self.portfolio.add_cash(cash)

    def setup(self, params=None):
        valid_data = TraderSchema(unknown=EXCLUDE).load(params)
        self.portfolio.add_cash(valid_data['starting_balance'])
        self.description = valid_data.get('description', '')
        self.params = params

    def get_name(self):
        raise NotImplementedError()

    def process_day(self, current_date, datasets, simulation_trade_id):
        raise NotImplementedError()
    
    def get_schema(self):
        return TraderSchema()

    def get_portfolio(self):
        return self.portfolio

    def buy(self, symbol, quantity, simulation_trade_id):
        self.simulator.buy(self, symbol, quantity, simulation_trade_id)
    
    def sell(self, symbol, quantity, simulation_trade_id):
        self.simulator.sell(self, symbol, quantity, simulation_trade_id)
    
    def print_portfolio(self, todays_prices):
        self.portfolio.print_portfolio(todays_prices, self.get_name())
    
    def print_profit(self, todays_prices):
        print ('Profit For {}: {:.2f}'.format(self.get_name(), self.portfolio.get_profit(todays_prices)))
