import os
import sys, inspect, importlib
import datetime
import memcache

import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API, DB

import app_config
from simulator import Simulator
from traders.interface import TraderInterface
from database.trader import get_traders
from database.simulation import add_simulation, add_simulation_trader, get_simulations, get_simulation_traders, get_transactions

EXECUTOR = ThreadPoolExecutor(2)

class SimulationRunSchema(Schema):
    trader_id = fields.Integer(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    starting_cash = fields.Int(required=True)
    description = fields.String(default="None Specified")
    # TODO params
    # TODO datasets

@API.route('/simulation', methods=['GET', 'POST'])
class SimulationHandler (restful.Resource):
    def get(self):
        return success(get_simulations(DB))

    def post(self):
        data = request.get_json(force=True)
        valid_data = SimulationRunSchema().load(data)
        valid_data['params'] = {}
        valid_data['simulation'] = add_simulation(DB,
                                                  valid_data['start_date'], 
                                                  valid_data['end_date'],
                                                  valid_data['starting_cash'],
                                                  datetime.datetime.now(),
                                                  valid_data['description'])
        DB.commit()
        mem = memcache.Client([(app_config.MEMCACHE_HOST, app_config.MEMCACHE_PORT)])
        progress = mem.set('progress_{}'.format(valid_data['simulation'].simulation_id), 'Requested')
        EXECUTOR.submit(self.run_simulation, valid_data)
        return success(valid_data['simulation'].simulation_id)


    def run_simulation(self, data):
        try:
            engine = create_engine('{}://{}:{}@{}/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_HOST, app_config.DB_NAME))
            engine.connect()
            Session = sessionmaker(bind=engine)
            session = Session()
            print(data)

            simulator = Simulator(session=session)
            # TODO multiple traders support
            # TODO trader config support
            traders = simulator.initiate_traders({data['trader_id']: dict(starting_cash=data['starting_cash'])})

            sim_traders = dict()
            session.commit()
            for trader in traders:
                sim_trader = add_simulation_trader(session, data['simulation'].simulation_id, trader.trader_id)
                session.commit()
                sim_traders[sim_trader] = trader
            simulator.start(data['start_date'], data['end_date'], sim_traders, data['simulation'].simulation_id)

            # TODO return results through get call

        except Exception as e:
            print(e)
        finally:
            session.close()

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
        return success(get_simulation_traders(DB, simulation_id=simulation_id))
