import os

import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API, DB


class TraderEditSchema(Schema):
    name = fields.String(required=True)

class TraderAddSchema(TraderEditSchema):
    location = fields.String(required=True)


@API.route('/trader', methods=['GET', 'POST'])
class TraderHandler (restful.Resource):
    def get(self):
        traders = DB.get_traders()
        if not request.args:
            for trader in traders:
                del trader['location']
            return success(traders)
        elif request.args['location'] == 'disk':
            files = os.listdir('traders')
            trader_files = []
            existing_files = []
            for trader in traders:
                if trader['location'][:7] == 'file://':
                    existing_files.append(trader['location'][7:])
            for filename in files:
                if filename[-3:] == '.py' and filename != 'interface.py' and filename not in existing_files:
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

        DB.add_trader(valid_data['name'], valid_data['location'])
        DB.commit()
        return success()

@API.route('/trader/<int:trader_id>', methods=['PUT', 'DELETE'])
class TraderEditHandler (restful.Resource):
    def put(self, trader_id):
        # TODO permissions / validation
        data = request.get_json(force=True)
        valid_data = TraderEditSchema().load(data)
        DB.edit_trader(trader_id, valid_data['name'])
        DB.commit()
        return success()

    def delete(self, trader_id):
        # TODO permissions / validation
        DB.delete_trader(trader_id)
        DB.commit()
        return success()
