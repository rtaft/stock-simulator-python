import datetime
import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API

import app_config
from database.company import find_company_by_symbol
from database.price_history import get_price_history

@API.route('/stock/history', methods=['GET'])
class StockHistoryHandler (restful.Resource):
    def get(self):
        symbols = request.args['symbols'].split(',')
        start_date = request.args['start_date']
        end_date = request.args['end_date']
        companies = find_company_by_symbol(flask.g.db, symbols)
        company_ids = [company.company_id for company in companies]
        
        history = get_price_history(session=flask.g.db, company_ids=company_ids, start_date=start_date, end_date=end_date)
        if not history:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d') - datetime.timedelta(days=3)
            history = get_price_history(session=flask.g.db, company_ids=company_ids, start_date=start_date, end_date=end_date)
        
        converted = dict()
        for company_id, data in history.items():
            new_data = dict()
            converted[company_id] = new_data
            for trade_date, trade in data.items():
                new_data[trade_date.strftime('%Y-%m-%d')] = dict(trade)
        return success(converted)
