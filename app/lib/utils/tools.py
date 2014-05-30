# -*- encoding: utf-8 -*-
import re
import datetime
from datetime import timedelta
from functools import update_wrapper
from bson.objectid import ObjectId
from flask import Response, make_response, request, current_app
from pysimplelogs.logger import SimpleLogger
from config import SIMPLELOGS_URL, DEBUG, MODULE_NAME
from version import version

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError


class MongoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return unicode(obj)
        return json.JSONEncoder.default(self, obj)

 
def jsonify(*args, **kwargs):
    """ jsonify with support for MongoDB ObjectId
    """
    meta = {'meta': {'status': 'ok'}}
    data = dict(*args, **kwargs)
    data.update(meta)
    return Response(json.dumps(data, cls=MongoJsonEncoder, ensure_ascii=False, indent=0),
                    mimetype='application/json',
                    content_type='application/json; charset=utf-8')


def prepare_find_params(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) or isinstance(value, unicode):
                data[key] = re.compile(value, re.IGNORECASE)
    elif isinstance(data, str) or isinstance(data, unicode):
        data = re.compile(data, re.IGNORECASE)
    return data


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


logger = SimpleLogger.get_logger(SIMPLELOGS_URL,
                                 MODULE_NAME,
                                 dict(name=MODULE_NAME, version=version),
                                 DEBUG)