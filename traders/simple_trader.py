from tools import get_simple_moving_average
from traders.interface import TraderInterface

import app_config
import tools

class SimpleTrader(TraderInterface):
    def setup(self):
        print('Setup called')

    def get_name(self):
        return 'Simple Trader'

    def process_day(self, current_date, dataset):
        # TODO gets stuck in infinate loop somewhere.

        # check state of existing stock holdings
            # sell stock if necessary
        ignore = []
        for holding in self.portfolio.get_stock_holdings_list():
            current_value = dataset.get(holding.symbol).price_history[current_date]['trade_close'] * holding.quantity
            #print('{} vs {}'.format(current_value, holding.cost_basis))
            if current_value > (holding.cost_basis * 1.5) or current_value < (holding.cost_basis * 0.8):
                self.simulation.sell(self.portfolio, holding.symbol, holding.quantity)
                ignore.append(holding.symbol)
        # check if we have enough money to spend
            # for each available stock
                # check whether we want to buy it
        to_buy = 3 - len(self.portfolio.stock_holdings)
        while to_buy and self.portfolio.cash > 333:
            best_slope = 0
            best_company = None
            for symbol, company in dataset.items():
                if (len(company.price_history) > 50 and symbol not in ignore):
                    sma20 = get_simple_moving_average(company.price_history, 20, 1)[0]
                    sma50 = get_simple_moving_average(company.price_history, 50, 1)[0]
                    slope = (sma50 - sma20) / sma20
                    if slope > best_slope:
                        best_slope = slope
                        best_company = company
            if best_company:
                if len(self.portfolio.stock_holdings) < 3:
                    max_sale = self.portfolio.cash / (3 - len(self.portfolio.stock_holdings))
                    quantity = (max_sale - app_config.TRADE_FEES) // best_company.price_history[current_date]['trade_close']
                    self.simulation.buy(self.portfolio, best_company.symbol, quantity)
                    ignore.append(best_company.symbol)
                    to_buy -= 1
            else:
                to_buy = 0
