from traders.interface import TraderInterface
import app_config

class Test(TraderInterface):
    def setup(self):
        print('Setup called')

    def get_name(self):
        return 'Apple Trader'

    def process_day(self, current_date, dataset):
        apple = dataset.get('AAPL')
        if apple:
            if current_date in apple.price_history and (self.portfolio.cash - app_config.TRADE_FEES) > apple.price_history[current_date]['trade_close']:
                quantity = (self.portfolio.cash - app_config.TRADE_FEES) // apple.price_history[current_date]['trade_close']
                self.simulation.buy(self.portfolio, 'AAPL', quantity)
        