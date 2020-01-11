import datetime
import decimal
import json
import random
import re

import flask

from database.database import Base

######################################################################################
# Generic Constants
######################################################################################
CONTENT_TYPE_TEXT = 'text/plain'
CONTENT_TYPE_JSON = 'application/json; charset=utf-8'


# Class to encode datetime.date/datetime.datetime as strings in ISO 8601 format
# and PostgreSQL Decimal -> float
# used by a json.dumps() call
class DateDecimalEncoder(json.JSONEncoder):
    """
    Class to encode datetime.date/datetime.datetime as strings in ISO 8601 format
    and PostgreSQL Decimal -> float
    used by a json.dumps() call
    """
    def default(self, obj):
        """
        Formats dates
        :param obj: object to format
        :return: Formatted object
        """
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

######################################################################################
# Utilities
######################################################################################


def make_response_object(headers, response_code, body):
    """
    Format response according to accept header.
    Build a Response() object from body/response code. Set any headers appropriately.
    :param headers: Dictionary of HTTP headers to return.
    :param response_code: HTTP Status code to return.
    :param body: Response body, in it's proper format (CSV, PDF, JSON etc.)
    :returns: Flask Response Object
    """
    response = flask.Response(body)
    response.status_code = response_code
    for header, value in headers.items():
        response.headers[header] = value
    return response


def make_json_response(response_code, body):
    """
    Format response according to accept header.
    Build a Response() object from body/response code.
    Sets headers to application/json
    :param response_code: HTTP Status code to return.
    :param body: Response body, in it's proper format (CSV, PDF, JSON etc.)
    :returns: Flask Response Object
    """
    headers = {'Content-Type': CONTENT_TYPE_JSON}
    if not isinstance(body, str):
        body = json.dumps(body, cls=DateDecimalEncoder)
    return make_response_object(headers, response_code, body)


def make_http_error_response(http_error):
    """
    Build a Response() object from HttpError and subclasses
    Sets headers to application/json
    :param http_error: HttpError from exceptions.py
    :returns: Flask Response Object
    """

    return make_json_response(http_error.response_code, json.dumps(http_error.body))


def success(body=None):
    """
    Creates a hashed success response
    :param body: Response body
    :return: Flask Response Object
    """
    if isinstance(body, (Base)):
        obj = dict(body.__dict__)
        del obj['_sa_instance_state']
        return make_json_response(200, obj)

    if isinstance(body, (list)):
        if len(body) > 0:
            if isinstance(body[0], (Base)):
                data = []
                for item in body:
                    obj = dict(item.__dict__)
                    del obj['_sa_instance_state']
                    data.append(obj)
                return make_json_response(200, data)

    return make_json_response(200, body)

def created(body=None):
    """
    Creates a created response
    :param body: Response body
    :return: Flask Response Object
    """
    return make_json_response(201, body)


def unmodified(body=None):
    """
    Creates an unmodified response
    :param body: Response body
    :return:Flask Response Object
    """
    return make_json_response(304, body)