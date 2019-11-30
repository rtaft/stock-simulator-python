import os
import sys, inspect, importlib

import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate
from concurrent.futures import ThreadPoolExecutor

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API, DB

import app_config
from database.mysql_db import MySQLDatabase
import simulator
from traders.interface import TraderInterface

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
        # TODO simulation ID
        EXECUTOR.submit(self.run_simulation, valid_data)
        valid_data['starting_cash'] = 10000
        valid_data['params'] = {}

    def run_simulation(self, data):
        try:
            database = MySQLDatabase()
            database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
            print(database.get_traders(trader_ids=[data['trader_id']]))

            traders = database.get_traders(trader_ids=[data['trader_id']])
            trader_instances = []
            sim = simulator.Simulator(database=database)
            for trader in traders:
                if trader['location'][:7] == 'file://':
                    path = 'traders.{}'.format(trader['location'][7:-3])
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
            database.close()

    def get_class(self, kls ):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m