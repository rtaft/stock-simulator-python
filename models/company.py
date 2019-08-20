class Company:
    def __init__(self, symbol, company_id):
        self.symbol = symbol
        self.company_id = company_id
        self.info = None  # Company DB opbject
        self.dividend_history = {}
        self.price_history = {}
        self.split_history = {}

