from flask import Flask, request
import flask
from flask_restful import Api
import requests
from functools import wraps
import threading

from api.exceptions import HttpError
from api import helpers

import app_config
from database.mysql_db import MySQLDatabase

APP = Flask(__name__)
API = Api(APP)
DB = MySQLDatabase()

@APP.before_request
def setup():
    #TODO how to handle this multithreaded
    DB.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)


@APP.teardown_request
def teardown(response):
    DB.close()

@APP.errorhandler(HttpError)
def handle_http_error(http_error):
    """
    Handles all HttpErrors thrown during a request
    :param http_error: The error to handle
    :return: The HTTP response to be sent to the client.
    """
    #log_error(http_error.body, error_code=http_error.response_code)
    print(http_error.body)
    print(http_error.response_code)
    return helpers.make_http_error_response(http_error)

def api_route(*args, **kwargs):
    """
    Decorator used to bind a URL path to a class
    :param args: Paths assigned to this class
    :param kwargs: Options for FlaskRESTful add_resource method
    :return: The method to be called when this decorator is accessed
    """
    def wrapper(cls):
        """
        Registers the class with FlaskRESKful to handle the path(s) specified
        :param cls: Class handing the request
        :return: The class
        """
        paths = []
        for path in list(args):
            if path in [None, '', '/']:
                raise ValueError("Path is missing or invalid")
            if path[0] == '/':
                path = path[1:]
            paths.append('/api/{0}'.format(path))

        API.add_resource(cls, *paths, **kwargs)
        return cls
    return wrapper


API.route = api_route