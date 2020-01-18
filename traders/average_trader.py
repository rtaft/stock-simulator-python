from tools import get_simple_moving_average
from traders.interface import TraderInterface

import app_config
import tools

class AverageTrader(TraderInterface):
    def setup(self, params=None):
        print('Setup called')

    def get_name(self):
        return 'Average Trader'

    def process_day(self, current_date, datasets, simulation_trade_id):
        # TODO gets stuck in infinate loop somewhere.

        # check state of existing stock holdings
            # sell stock if necessary
        ignore = []
        for holding in self.portfolio.get_stock_holdings_list():
            if datasets.get(holding.symbol).price_history.get(current_date, {}).trade_close:
                current_value = datasets.get(holding.symbol).price_history[current_date].trade_close * holding.quantity
                #print('{} vs {}'.format(current_value, holding.cost_basis))
                if current_value > (holding.cost_basis * 1.5) or current_value < (holding.cost_basis * 0.8):
                    self.sell(holding.symbol, holding.quantity, simulation_trade_id)
                    ignore.append(holding.symbol)
            else:
                print('No History for {} on {}'.format(holding.symbol, current_date))

        # check if we have enough money to spend
            # for each available stock
                # check whether we want to buy it
        to_buy = 3 - len(self.portfolio.stock_holdings)

        while to_buy and self.portfolio.cash > 333:
            best_slope = 0
            best_company = None
            max_sale = (self.portfolio.cash - app_config.TRADE_FEES) / to_buy
            
            for symbol, company in datasets.items():
                if company.price_history.get(current_date, {}).get('trade_close', 0) > 1 and \
                   company.price_history.get(current_date, {}).get('trade_close', 0) < max_sale and \
                   len(company.price_history) > 50 and \
                   symbol not in ignore:
                    sma20 = get_simple_moving_average(company.price_history, 20, 1)[0]
                    sma50 = get_simple_moving_average(company.price_history, 50, 1)[0]
                    if sma20 and sma50:
                        slope = (sma50 - sma20) / sma20
                        if slope > best_slope:
                            best_slope = slope
                            best_company = company
            if best_company:
                print(best_company.symbol)
                #if best_company.symbol == 'FLUX':
                #    print(best_company.price_history)
                quantity = max_sale // best_company.price_history[current_date]['trade_close']
                self.buy(best_company.symbol, quantity, simulation_trade_id)
                ignore.append(best_company.symbol)
                to_buy -= 1
            else:
                to_buy = 0
