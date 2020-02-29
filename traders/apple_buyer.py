from traders.interface import TraderInterface

import app_config
import tools

class AppleBuyer(TraderInterface):
    def setup(self, params=None):
        print('Setup called')

    def get_name(self):
        return 'Apple Trader'

    def process_day(self, current_date, datasets, simulation_trade_id):
        apple = datasets.get('AAPL')
        if apple:
            current_price = apple.get_current_price()
            if current_price and (self.portfolio.cash - app_config.TRADE_FEES) > current_price.trade_close:
                quantity = (self.portfolio.cash - app_config.TRADE_FEES) // current_price.trade_close
                self.buy('AAPL', quantity, simulation_trade_id)
        