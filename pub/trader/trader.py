import os

import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate
from marshmallow_jsonschema import JSONSchema

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API

from database.trader import get_traders, add_trader, delete_trader
from traders.util import initiate_traders

class TraderEditSchema(Schema):
    name = fields.String(required=True)

class TraderAddSchema(TraderEditSchema):
    location = fields.String(required=True)


@API.route('/trader', methods=['GET', 'POST'])
class TraderHandler (restful.Resource):
    def get(self):
        traders = get_traders(flask.g.db)
        if not request.args:
            for trader in traders:
                del trader.location
            return success(traders)
        elif request.args['location'] == 'disk':
            files = os.listdir('traders')
            trader_files = []
            existing_files = []
            for trader in traders:
                if trader.location[:7] == 'file://':
                    existing_files.append(trader.location[7:])
            for filename in files:
                if filename[-3:] == '.py' and filename != 'interface.py' and filename != 'util.py' and filename not in existing_files:
                    trader_files.append(filename)

            return success(trader_files)
        else:
            raise NotFound()
    
    def post(self):
        data = request.get_json(force=True)
        valid_data = TraderAddSchema().load(data)

        # local:  file://tradername.py
        # github: TODO https://github.com/project (other repo)
        # upload: TODO

        #TODO validate it doesn't already exist?

        add_trader(flask.g.db, valid_data['name'], valid_data['location'])
        flask.g.db.commit()
        return success()

@API.route('/trader/<int:trader_id>', methods=['PUT', 'DELETE'])
class TraderEditHandler (restful.Resource):
    def put(self, trader_id):
        # TODO permissions / validation
        data = request.get_json(force=True)
        valid_data = TraderEditSchema().load(data)
        trader = get_traders(flask.g.db, trader_ids=[trader_id])
        if trader:
            trader[0].name = valid_data['name']
            flask.g.db.commit()
            return success()
        raise NotFound()

    def delete(self, trader_id):
        # TODO permissions / validation
        delete_trader(flask.g.db, trader_id)
        flask.g.db.commit()
        return success()

@API.route('/trader/<int:trader_id>/schema', methods=['GET'])
class TraderSchemaHandler (restful.Resource):
    def get(self, trader_id):
        traders = get_traders(flask.g.db, trader_ids=[trader_id])
        instances = initiate_traders(None, traders)
        if instances[0] and instances[0].get_schema():
            trader_data = list(JSONSchema().dump(instances[0].get_schema())['definitions'].values())[0]['properties']
            for trader, data in trader_data.items():
                data['required'] = trader in list(JSONSchema().dump(instances[0].get_schema())['definitions'].values())[0]['required']
                if isinstance(data['type'], list):
                    data['type'].remove('null')
                    if len(data['type']) == 1:
                        data['type'] = data['type'][0]
            return success(trader_data)
        return success()