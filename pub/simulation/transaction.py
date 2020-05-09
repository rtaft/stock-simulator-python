import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API

import app_config
from database.simulation import get_transactions

@API.route('/transaction/<int:sim_trader_id>', methods=['GET'])
class TransactionHandler (restful.Resource):
    def get(self, sim_trader_id):
        transactions = []
        
        for transaction, symbol in get_transactions(flask.g.db, sim_trader_id):
            transactions.append(transaction)
            transaction.__dict__['symbol'] = symbol
        
        return success(transactions)
