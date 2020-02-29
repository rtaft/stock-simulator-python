import math
import numpy

def get_simple_moving_average(price_history, company_id, period, days):
    company_price_history = price_history.get_last_n_days(company_id, period + days)
    dates = sorted(list(company_price_history.keys()))
    values = [company_price_history[trade_date].trade_close for trade_date in dates]
    moving_average = []
    for i in range(1, period+1):
        moving_average.append(sum(values[i: i+days])/days)
    return moving_average


def bollinger_bands(price_history, company_id, period, days=20, stdv=2):
    company_price_history = price_history.get_last_n_days(company_id, period + days)
    dates = sorted(list(company_price_history.keys()))
    values = [company_price_history[trade_date].trade_close for trade_date in dates]
    sma = get_simple_moving_average(price_history, company_id, period + days, days)
    
    bands = []
    for i in range(days, days + period):
        deviation = stdv * numpy.std(values[i-days+1: i+1])
        top = sma[i] + deviation
        bottom = sma[i] - deviation
        bands.append((deviation, top, bottom))
    return bands
