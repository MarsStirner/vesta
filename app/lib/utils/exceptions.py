# -*- coding: utf-8 -*-
from flask import Response, make_response
from .tools import json
from app.app import app


class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidAPIUsage)
def handle_invalid_usage(error):
    meta = {'status': 'error'}
    meta.update(error.to_dict())
    return Response(json.dumps({'meta': meta}, ensure_ascii=False, indent=0),
                    mimetype='application/json',
                    content_type='application/json; charset=utf-8', status=error.status_code)


@app.errorhandler(404)
def not_found(error):
    return Response(json.dumps({'meta': {'status': 'error', 'message': 'Not found'}}, ensure_ascii=False, indent=0),
                    mimetype='application/json',
                    content_type='application/json; charset=utf-8', status=404)