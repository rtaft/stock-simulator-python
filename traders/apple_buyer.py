from traders.interface import TraderInterface

import app_config
import tools

class AppleBuyer(TraderInterface):
    def setup(self, params=None):
        print('Setup called')

    def get_name(self):
        return 'Apple Trader'

    def process_day(self, current_date, datasets):
        apple = datasets.get('AAPL')
        if apple:
            #tools.get_moving_average(apple.price_history, 60, 30)
            tools.bollinger_bands(apple.price_history, 60, 20)
            if current_date in apple.price_history and (self.portfolio.cash - app_config.TRADE_FEES) > apple.price_history[current_date].trade_close:
                quantity = (self.portfolio.cash - app_config.TRADE_FEES) // apple.price_history[current_date].trade_close
                self.simulator.buy(self, 'AAPL', quantity)
        