from marshmallow import Schema, fields, validate, EXCLUDE

from tools import get_simple_moving_average
from traders.interface import TraderInterface, TraderSchema

import app_config
import tools

class SimpleTraderSchema(TraderSchema):
    max_holdings = fields.Integer(required=True, metadata=dict(fieldname="Max Holdings", value=5, notes="Maximum number of stocks to hold in the portfolio."))
    loss_sell_ratio = fields.Number(required=True, metadata=dict(fieldname="Loss Sell Ratio", value=0.8, notes="Loss ratio before deciding to sell the stock. IE: 0.8 = 20% loss."))
    gain_sell_ratio = fields.Number(required=True, metadata=dict(fieldname="Gain Sell Ratio", value=1.5, notes="Profit ratio before deciding to sell the stock. IE: 1.5 = 50% gain."))
    minimum_transaction = fields.Integer(required=True, metadata=dict(fieldname="Minimum Transaction", value=500, notes="Minimum dollar value to spend on a stock."))

class SimpleTrader(TraderInterface):
    def setup(self, params):
        super(SimpleTrader, self).setup(params)
        valid_data = SimpleTraderSchema(unknown=EXCLUDE).load(params)
        self.max_holdings = valid_data.get('max_holdings')
        self.loss_sell_ratio = valid_data.get('loss_sell_ratio')
        self.gain_sell_ratio = valid_data.get('gain_sell_ratio')
        self.minimum_transaction = valid_data.get('minimum_transaction')
        self.profit_sale = dict()
        self.loss_sale = dict()

    def get_schema(self):
        return SimpleTraderSchema()

    def get_name(self):
        return 'Simple Trader'

    def process_day(self, current_date, datasets, simulation_trade_id):
        try:
            ignore = []
            for holding in self.portfolio.get_stock_holdings_list():
                if datasets.get(holding.symbol).get_current_price() and datasets.get(holding.symbol).get_current_price().trade_close:
                    current_value = datasets.get(holding.symbol).get_current_price().trade_close * holding.quantity

                    if (current_value > self.profit_sale[holding.symbol] * holding.quantity) or \
                        current_value < self.loss_sale[holding.symbol] * holding.quantity:
                        self.sell(holding.symbol, holding.quantity, simulation_trade_id)
                        # All stock sold, remove the symbol from both lists
                        del self.profit_sale[holding.symbol]
                        del self.loss_sale[holding.symbol]
                        ignore.append(holding.symbol)
                else:
                    print('No History for {} on {}'.format(holding.symbol, current_date))
            to_buy = self.max_holdings - len(self.portfolio.stock_holdings)
            # TODO Rank the stocks, loop once, then pick.
            while to_buy and self.portfolio.cash > self.minimum_transaction:
                best_slope = 0
                best_company = None
                max_sale = (self.portfolio.cash - app_config.TRADE_FEES) / to_buy

                for symbol, company in datasets.items():
                    # len(company.price_history) > 50 and \ TODO how to process
                    if company.get_current_price() and \
                    company.get_current_price().trade_close > 1 and \
                    company.get_current_price().trade_close < max_sale and \
                    symbol not in ignore and symbol not in [holding.symbol for holding in self.portfolio.get_stock_holdings_list()]:
                        sma20 = get_simple_moving_average(company.price_history, company.company.company_id, 20, 1)[0]
                        sma50 = get_simple_moving_average(company.price_history, company.company.company_id, 50, 1)[0]
                        if sma20 and sma50:
                            slope = (sma20 - sma50) / sma50
                            if slope > best_slope:
                                best_slope = slope
                                best_company = company
                if best_company:
                    quantity = max_sale // best_company.get_current_price().trade_close
                    self.buy(best_company.company.symbol, quantity, simulation_trade_id)
                    self.profit_sale[best_company.company.symbol] = best_company.get_current_price().trade_close * self.gain_sell_ratio
                    self.loss_sale[best_company.company.symbol] =  best_company.get_current_price().trade_close * self.loss_sell_ratio
                    ignore.append(best_company.company.symbol)
                    to_buy -= 1
                else:
                    to_buy = 0
        except Exception as e:
            import traceback
            print(e)
            traceback.print_exc()