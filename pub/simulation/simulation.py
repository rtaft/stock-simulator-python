import os
import sys, inspect, importlib

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
import simulator
from traders.interface import TraderInterface
from database.trader import get_traders
from database.simulation import add_simulation

EXECUTOR = ThreadPoolExecutor(2)

class SimulationRunSchema(Schema):
    trader_id = fields.Integer(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    # TODO starting cash
    # TODO params
    # TODO datasets

@API.route('/simulation', methods=['GET', 'POST'])
class SimulationHandler (restful.Resource):
    def get(self):
        pass

    def post(self):
        data = request.get_json(force=True)
        valid_data = SimulationRunSchema().load(data)
        valid_data['starting_cash'] = 10000 #TODO
        valid_data['description'] = 'Temp Description' #TODO
        valid_data['params'] = {}
        simulation = add_simulation(DB,
                                    valid_data['start_date'], 
                                    valid_data['end_date'],
                                    valid_data['starting_cash'],
                                    datetime.datetime.now(),
                                    valid_data['trader_id'],
                                    valid_data['description'])
        valid_data['simulation_id'] = simulation.simulation_id
        # TODO simulation ID
        EXECUTOR.submit(self.run_simulation, valid_data)
        return success(simulation.simulation_id)


    def run_simulation(self, data):
        try:
            engine = create_engine('{}://{}:{}@localhost/{}'.format(app_config.DB_TYPE, app_config.DB_USER, app_config.DB_PASS, app_config.DB_NAME))
            engine.connect()
            Session = sessionmaker(bind=engine)
            session = Session()

            traders = get_traders(session, trader_ids=[data['trader_id']])
            trader_instances = []
            sim = simulator.Simulator(session=session)
            for trader in traders:
                if trader.location[:7] == 'file://':
                    path = 'traders.{}'.format(trader.location[7:-3])
                    importlib.import_module(path)
                    trader_module = self.get_class(path)
                    for name, obj in inspect.getmembers(trader_module):
                        if inspect.isclass(obj):
                            if obj != TraderInterface:
                                for mro in inspect.getmro(obj):
                                    if mro == TraderInterface:
                                        print('Adding {}'.format(name))
                                        trader = obj(sim, cash=data['starting_cash'])
                                        trader.setup(data['params'])
                                        trader_instances.append(trader)
            print(data)
            sim.start(data['start_date'], data['end_date'], trader_instances)
            # TODO store simulation results
            # TODO store current progress
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