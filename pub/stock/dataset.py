import flask
from flask import request
import flask_restful as restful

from api.helpers import success, created
from api.restful import API, DB

from database.stock import get_stock_lists

@API.route('/stock/dataset', methods=['GET'])
class DatasetHandler (restful.Resource):
    def get(self):
        names = ['All']
        for stock_list in get_stock_lists(DB):
            names.append(stock_list.name)
        return success(names)
