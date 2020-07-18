import os
import sys, inspect, importlib
import datetime
import memcache

import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate
from concurrent.futures import ThreadPoolExecutor
from flask_socketio import send, emit, join_room, leave_room
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API, APP, SOCK

import app_config
from simulator import Simulator
from traders.interface import TraderInterface
from database.trader import get_traders
from database.simulation import add_simulation, add_simulation_trader, get_simulations, get_simulation_traders, get_transactions
from traders.util import initiate_traders

EXECUTOR = ThreadPoolExecutor(2)

class SimulationRunSchema(Schema):
    traders = fields.List(fields.Dict(required=True))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    description = fields.String(missing="None Specified")
    stock_list = fields.String(required=True, metatdata="Dataset to run against.")

@API.route('/simulation', methods=['GET', 'POST'])
class SimulationHandler (restful.Resource):
    def get(self):
        return success(get_simulations(flask.g.db))

    def post(self):
        data = request.get_json(force=True)
        valid_data = SimulationRunSchema().load(data)
        valid_data['simulation'] = add_simulation(flask.g.db,
                                                  valid_data['start_date'], 
                                                  valid_data['end_date'],
                                                  datetime.datetime.now(),
                                                  valid_data['description'],
                                                  valid_data['stock_list'])
        flask.g.db.commit()
        mem = memcache.Client([(app_config.MEMCACHE_HOST, app_config.MEMCACHE_PORT)])
        mem.set('progress_{}'.format(valid_data['simulation'].simulation_id), 'Requested')
        EXECUTOR.submit(self.run_simulation, valid_data)
        return success(valid_data['simulation'].simulation_id)


    def run_simulation(self, data):
        try:
            engine = create_engine('{}://{}:{}@{}/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_HOST, app_config.DB_NAME))
            engine.connect()
            Session = sessionmaker(bind=engine)
            session = Session()
            simulator = Simulator(session=session, stock_list_name=data['stock_list'])
            traders = simulator.create_traders(data['traders'])

            sim_traders = dict()
            session.commit()
            for trader in traders:
                sim_trader = add_simulation_trader(session, data['simulation'].simulation_id, trader.trader_id,
                                                   starting_balance=trader.get_portfolio().get_cash_balance())
                session.commit()
                sim_traders[sim_trader] = trader
            simulator.start(data['start_date'], data['end_date'], sim_traders, data['simulation'].simulation_id, self.callback)

        except Exception as e:
            print(e)
        finally:
            session.close()

    def callback(self, simulation_id, message):
        try:
            with APP.test_request_context('/api/simulation'):
                SOCK.emit('/simulation/{}'.format(simulation_id), '{}'.format(message))
        except Exception as e:
            print (e)



    def get_class(self, kls ):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

@API.route('/simulation/<int:simulation_id>/status', methods=['GET'])
class SimulationStatusHandler (restful.Resource):
    def get(self, simulation_id):
        mem = memcache.Client([(app_config.MEMCACHE_HOST, app_config.MEMCACHE_PORT)])
        progress = mem.get('progress_{}'.format(simulation_id))
        if progress:
            return success(dict(status=progress))
        raise NotFound()

@API.route('/simulation/<int:simulation_id>', methods=['GET'])
class SimulationResultsHandler (restful.Resource):
    def get(self, simulation_id):
        return success(get_simulation_traders(flask.g.db, simulation_id=simulation_id))
