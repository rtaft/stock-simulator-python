import math
import numpy

def get_simple_moving_average(company_price_history, period, days):
    dates = list(company_price_history.keys())[-1 * (days + period):]
    values = [company_price_history[trade_date]['trade_close'] for trade_date in dates]
    moving_average = []
    for i in range(1, period+1):
        moving_average.append(sum(values[i: i+days])/days)
    return moving_average


def bollinger_bands(company_price_history, period, days=20, stdv=2):
    dates = list(company_price_history.keys())[-1 * (period + days):]
    values = [company_price_history[trade_date]['trade_close'] for trade_date in dates]
    sma = get_simple_moving_average(company_price_history, period + days, days)
    
    bands = []
    for i in range(days, days + period):
        deviation = stdv * numpy.std(values[i-days+1: i+1])
        top = sma[i] + deviation
        bottom = sma[i] - deviation
        bands.append((deviation, top, bottom))
    return bands
