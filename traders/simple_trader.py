from tools import get_simple_moving_average
from traders.interface import TraderInterface

import app_config
import tools

class SimpleTrader(TraderInterface):
    def setup(self, params=None):
        self.max_holdings = params.get('max_holding', 3)
        self.loss_sell_ratio = params.get('loss_sell_ratio', 0.8)
        self.gain_sell_ratio = params.get('gain_sell_ratio', 1.5)
        self.minimum_transaction = params.get('minimum_transaction', 333)

    def get_name(self):
        return 'Simple Trader'

    def process_day(self, current_date, datasets, simulation_trade_id):
        # TODO gets stuck in infinate loop somewhere.
        try:
            ignore = []
            for holding in self.portfolio.get_stock_holdings_list():
                if datasets.get(holding.symbol).get_current_price() and datasets.get(holding.symbol).get_current_price().trade_close:
                    current_value = datasets.get(holding.symbol).get_current_price().trade_close * holding.quantity
                    if current_value > (holding.cost_basis * self.gain_sell_ratio) or current_value < (holding.cost_basis * self.loss_sell_ratio):
                        self.sell(holding.symbol, holding.quantity, simulation_trade_id)
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
                    symbol not in ignore:
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
                    ignore.append(best_company.company.symbol)
                    to_buy -= 1
                else:
                    to_buy = 0
        except Exception as e:
            import traceback
            print(e)
            traceback.print_exc()