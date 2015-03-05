# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import g, make_response, abort, request
from app.lib.utils.exceptions import InvalidAPIUsage
from app.lib.data import Clients, DictionaryNames, Dictionary
from app.lib.utils.tools import jsonify, json, prepare_find_params, crossdomain, parse_request
from bson.objectid import InvalidId
from ..app import module

"""API для работы с конкретным справочником"""
#decorators = [user_required]
decorators = [crossdomain]


base_url = '/v1/<string:code>/'


@module.route(base_url, methods=['GET'])
@module.route(base_url + '<document_id>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
def dictionary_get(code, document_id=None):
    if document_id is None:
        return list_documents(code)
    else:
        result = document_details(code, document_id)
        if not result:
            abort(404)
        return jsonify(data=result)


def list_documents(code, find=None):
    try:
        obj = Dictionary(code)
        result = obj.get_list(find)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    return jsonify(data=list(result))


def document_details(code, document_id):
    try:
        obj = Dictionary(code)
        #TODO: учесть auth_token
        result = obj.get_document(dict(_id=document_id))
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except InvalidId, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    return result


@module.route(base_url + '<string:field>/<string:field_value>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
def document_by_field(code, field, field_value):
    if field == 'id':
        field_value = int(field_value)
    try:
        obj = Dictionary(code)
        result = obj.get_document({str(field): field_value})
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except InvalidId, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    else:
        if not result:
            abort(404)
    return make_response(jsonify(dict(data=result)), 200)


@module.route(base_url, methods=['POST'])
@crossdomain('*', methods=['POST'])
def dictionary_post(code):
    data = parse_request(request)
    try:
        obj = Dictionary(code)
        _id = obj.add_documents(data)
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    else:
        if _id:
            if isinstance(_id, list):
                _id = [str(i) for i in _id]
            else:
                _id = str(_id)
            return make_response(jsonify(dict(_id=_id)), 201)
        raise InvalidAPIUsage(u'Ошибка добавления данных', 500)


@module.route(base_url + '<document_id>/', methods=['PUT'])
@crossdomain('*', methods=['PUT'])
def dictionary_put(code, document_id):
    data = parse_request(request)
    try:
        obj = Dictionary(code)
        exists = obj.exists(dict(_id=document_id))
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    try:
        data.update(dict(_id=document_id))
        result = obj.add_document(data)
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    if not exists:
        return make_response(jsonify(dict(_id=result)), 201)
    return make_response(jsonify(), 200)


@module.route(base_url + '<document_id>/', methods=['DELETE'])
@crossdomain('*', methods=['DELETE'])
def dictionary_delete(code, document_id):
    try:
        obj = Dictionary(code)
        obj.delete(_id=document_id)
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except RuntimeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    return make_response(jsonify(), 204)


@module.route('/find/<code>/', methods=['POST'])
@crossdomain('*', methods=['POST'])
def find_data(code):
    data = parse_request(request)
    obj_names = DictionaryNames()
    try:
        obj = Dictionary(code)
        _dict = obj_names.get_by_code(code)
        result = obj.get_list(prepare_find_params(data))
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except InvalidId, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    else:
        ret_data = _dict
        if not result:
            ret_data.update(dict(data={}))
            return make_response(jsonify(ret_data), 200)
        ret_data.update(dict(data=result))
    return make_response(jsonify(ret_data), 200)