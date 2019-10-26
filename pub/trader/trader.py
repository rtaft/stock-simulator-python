import os

import flask
from flask import request
import flask_restful as restful

from api.helpers import success, created
from api.restful import API, DB

@API.route('/trader', methods=['GET'])
class TraderHandler (restful.Resource):
    def get(self):
        files = os.listdir('traders')
        trader_files = []
        for filename in files:
            if filename[-3:] == '.py' and filename != 'interface.py':
                trader_files.append(filename)

        return success(trader_files)