from traders.interface import TraderInterface, TraderSchema, EXCLUDE
from marshmallow import Schema, fields, validate
import app_config
import tools


class SingleBuyerSchema(TraderSchema):
    symbol = fields.String(required=True, metadata=dict(notes="Symbol of the stock to buy."))

class SingleBuyer(TraderInterface):
    def setup(self, params):
        super(SingleBuyer, self).setup(params)
        valid_data = SingleBuyerSchema(unknown=EXCLUDE).load(params)
        self.symbol = valid_data.get('symbol')

    def get_schema(self):
        return SingleBuyerSchema()

    def get_name(self):
        return 'Single Buyer'

    def process_day(self, current_date, datasets, simulation_trade_id):
        apple = datasets.get(self.symbol)
        if apple:
            current_price = apple.get_current_price()
            if current_price and (self.portfolio.cash - app_config.TRADE_FEES) > current_price.trade_close:
                quantity = (self.portfolio.cash - app_config.TRADE_FEES) // current_price.trade_close
                self.buy(self.symbol, quantity, simulation_trade_id)
