import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API

import app_config
from database.simulation import get_transactions, get_transactions_by_sim_trader, get_simulation_traders

@API.route('/transaction/<int:simulation_id>/<int:sim_trader_id>', methods=['GET'])
class TransactionTraderHandler (restful.Resource):
    def get(self, simulation_id, sim_trader_id):
        transactions = []
        
        for transaction, symbol in get_transactions(flask.g.db, sim_trader_id):
            transactions.append(transaction)
            transaction.__dict__['symbol'] = symbol
        
        return success(transactions)

@API.route('/transaction/<int:simulation_id>', methods=['GET'])
class TransactionHandler (restful.Resource):
    def get(self, simulation_id):
        sim_traders = get_simulation_traders(flask.g.db, simulation_id)
        transactions = get_transactions_by_sim_trader(flask.g.db, [trader['simulation_trader_id'] for trader in sim_traders])
        for sim_trader_id in transactions.keys():
            new_transactions = []
            for transaction, symbol in transactions[sim_trader_id]:
                new_transaction = dict(transaction.__dict__)
                new_transaction['symbol'] = symbol
                del new_transaction['_sa_instance_state']
                new_transactions.append(new_transaction)
            transactions[sim_trader_id] = new_transactions
        return success(transactions)