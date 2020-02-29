class DataSet:
    def __init__(self, company, price_history):
        self.company = company
        self.dividend_history = {}
        self.price_history = price_history
        self.split_history = {}

    def get_current_price(self):
        return self.price_history.get_current_price(self.company.company_id)