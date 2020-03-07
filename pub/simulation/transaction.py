import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API, DB

import app_config
from database.simulation import add_simulation, add_simulation_trader, get_simulations, get_simulation_traders, get_transactions

@API.route('/transaction/<int:sim_trader_id>', methods=['GET'])
class TransactionHandler (restful.Resource):
    def get(self, sim_trader_id):
        return success(get_transactions(DB, sim_trader_id))
