# -*- encoding: utf-8 -*-
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
    return Response(json.dumps(dict(*args, **kwargs), cls=MongoJsonEncoder, ensure_ascii=False, indent=0),
                    mimetype='application/json',
                    content_type='application/json; charset=utf-8')

logger = SimpleLogger.get_logger(SIMPLELOGS_URL,
                                 MODULE_NAME,
                                 dict(name=MODULE_NAME, version=version),
                                 DEBUG)