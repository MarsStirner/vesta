# -*- encoding: utf-8 -*-
import re
import datetime
from bson.objectid import ObjectId
from flask import Response
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
    return data


logger = SimpleLogger.get_logger(SIMPLELOGS_URL,
                                 MODULE_NAME,
                                 dict(name=MODULE_NAME, version=version),
                                 DEBUG)