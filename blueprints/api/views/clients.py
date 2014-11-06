# -*- coding: utf-8 -*-
from flask import make_response, request
from app.lib.utils.exceptions import InvalidAPIUsage
from app.lib.data import Clients
from app.lib.utils.tools import jsonify, parse_request, crossdomain
from ..app import module

"""API для работы с информацией о зарегистрированных клиентах (внешних системах)"""

base_url = '/clients/'


@module.route(base_url, methods=['GET'])
@module.route(base_url + '<code>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
def clients_get(code=None):
    """Получение списка клиентов или информации по конкретному клиенту"""
    collection = Clients()
    if code is None:
        # return list of Clients
        try:
            result = collection.get_list()
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except ValueError, e:
            return jsonify(dict())
        return jsonify(dict(data=list(result)))
    else:
        # return Dictionary info by code
        result = collection.get_by_code(code)
        if result is None:
            result = dict()
        return jsonify(result)


@module.route(base_url, methods=['POST'])
@crossdomain('*', methods=['POST'])
def clients_post():
    """Заведение информации о клиенте"""
    data = parse_request(request)
    obj = Clients()
    try:
        _id = obj.add(data)
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    else:
        if _id:
            return make_response(jsonify(dict(_id=str(_id))), 201)
        raise InvalidAPIUsage(u'Ошибка добавления данных', 500)


@module.route(base_url + '<code>/', methods=['PUT'])
@crossdomain('*', methods=['PUT'])
def clients_put(code):
    """Обновление информации о клиенте"""
    data = parse_request(request)
    obj = Clients()
    try:
        document = obj.get_by_code(code)
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    else:
        try:
            _id = obj.update(_id=document.get('_id'), data=data)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except AttributeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
    return make_response(jsonify(dict(_id=_id)), 200)


@module.route(base_url + '<code>/', methods=['DELETE'])
@crossdomain('*', methods=['DELETE'])
def clients_delete(code):
    """Удаление клиента"""
    obj = Clients()
    try:
        document = obj.get_by_code(code)
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    try:
        obj.delete(_id=document.get('_id'))
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except RuntimeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    return make_response(jsonify(), 204)