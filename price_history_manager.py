import datetime
from database.price_history import get_price_history as get_price_history_from_db


class PriceHistoryManager():

    def __init__(self, session, load_size=90):
        self.session = session
        self.current_date = None
        self.load_size = load_size
        self.last_days_load = None
        self.history = dict() # company_id : dict ( key, value )   prices=dict ( date : price ), start_loaded_date, end_loaded_date

    def initial_load(self, past_days=200, current_date=None):
        if current_date:
            self.current_date = current_date
        self.last_days_load = self.current_date + datetime.timedelta(days=self.load_size)
        start_date = self.current_date - datetime.timedelta(days=past_days)
        data = get_price_history_from_db(self.session, start_date=start_date, end_date=self.last_days_load)
        for company_id, price_data in data.items():
            company_history = self.history.setdefault(company_id, dict())
            # TODO individual start and end load dates
            company_history.setdefault('prices', dict()).update(price_data)
            company_history['start_loaded_date'] = start_date
            company_history['end_loaded_date'] = self.last_days_load

    def set_current_date(self, current_date):
        if self.current_date and current_date < self.current_date:
            raise Exception('Cannot set a past date.')
        self.current_date = current_date

    def get_current_date(self):
        return self.current_date

    def get_last_n_days(self, company_id, days):
        end_date = self.current_date - datetime.timedelta(days=days+self.load_size)
        data = self.get_price_history(company_id, end_date, self.current_date)
        temp_date = self.current_date
        temp_data = dict()
        while temp_date > end_date and len(temp_data) < days:
            if temp_date in data:
                temp_data[temp_date] = data[temp_date]
            temp_date = temp_date - datetime.timedelta(days=1)
        return temp_data

    def get_current_price(self, company_id):
        return self.get_price_history(company_id, self.current_date, self.current_date).get(self.current_date)
    
    def get_days_prices(self, company_ids=None):
        todays_prices = dict()
        if not self.last_days_load or self.current_date > self.last_days_load:
            self.last_days_load = self.current_date + datetime.timedelta(days=self.load_size)
            data = get_price_history_from_db(self.session, company_ids=company_ids, start_date=self.current_date, end_date=self.last_days_load)
            for company_id, price_data in data.items():
                company_history = self.history.setdefault(company_id, dict())
                # TODO individual start and end load dates
                company_history.setdefault('prices', dict()).update(price_data)
        
        for company_id, company_data in self.history.items():
            if 'prices' in company_data and self.current_date in company_data['prices']:
                todays_prices[company_id] = {self.current_date: company_data['prices'][self.current_date]}
        return todays_prices

    def get_price_history(self, company_id, start_date, end_date):
        if end_date > self.current_date:
            raise Exception('Cannot get a future price.')
        if start_date > end_date:
            raise Exception('Start date is greater than end date')
        
        company_history = self.history.setdefault(company_id, dict())

        
        load_data_start = None
        load_data_end = None

        if 'start_loaded_date' not in company_history or (start_date < company_history['start_loaded_date'] and end_date > company_history['end_loaded_date']):
            load_data_start = start_date
            load_data_end = end_date + datetime.timedelta(days=self.load_size)
        elif company_history['start_loaded_date'] < start_date < company_history['end_loaded_date'] and end_date > company_history['end_loaded_date']:
            load_data_start = company_history['end_loaded_date']
            load_data_end = end_date + datetime.timedelta(days=self.load_size)
        elif start_date < company_history['start_loaded_date'] and company_history['start_loaded_date'] < end_date < company_history['end_loaded_date']:
            load_data_start = start_date
            load_data_end = company_history['start_loaded_date']
        elif end_date < company_history['start_loaded_date']:
            load_data_start = start_date
            load_data_end = company_history['start_loaded_date']
        elif start_date > company_history['end_loaded_date']:
            load_data_start = company_history['end_loaded_date']
            load_data_end = end_date + datetime.timedelta(days=self.load_size)
        
        if load_data_start:
            print('Query {} {} {}'.format(company_id, load_data_start, load_data_end))
            loaded_data = get_price_history_from_db(session=self.session, company_ids=[company_id], start_date=load_data_start, end_date=load_data_end)
            if company_id in loaded_data:
                company_history.setdefault('prices', dict()).update(loaded_data[company_id])
                company_history['start_loaded_date'] = min(company_history.get('start_loaded_date', load_data_start), load_data_start)
                company_history['end_loaded_date'] = max(company_history.get('end_loaded_date', load_data_end), load_data_end)
            else:
                return dict()
        temp_history = dict()
        temp_date = start_date
        while temp_date <= end_date:
            if temp_date in company_history['prices']:
                temp_history[temp_date] = company_history['prices'][temp_date]
            temp_date = temp_date + datetime.timedelta(days=1)
        return temp_history
