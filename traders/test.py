from traders.interface import TraderInterface

class Test(TraderInterface):
    def setup(self):
        print('Setup called')

    def process_day(self, current_date, dataset):
        print ('Process Day {}'.format(current_date))
        apple = dataset.get('AAPL')
        if apple:
            if current_date in apple.price_history and self.portfolio.cash > apple.price_history[current_date]['trade_close']:
                quantity = self.portfolio.cash // apple.price_history[current_date]['trade_close']
                self.simulation.buy(self.portfolio, 'AAPL', quantity)
        