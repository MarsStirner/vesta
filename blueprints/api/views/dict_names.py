# -*- coding: utf-8 -*-
from flask import make_response, request
from app.lib.utils.exceptions import InvalidAPIUsage
from app.lib.data import DictionaryNames
from app.lib.utils.tools import jsonify, parse_request, crossdomain
from ..app import module


"""API для работы с информацией о справочниках"""

base_url = '/dictionaries/'


@module.route(base_url, methods=['GET'])
@module.route(base_url + '<code>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
def dictionaries_get(code=None):
    """Получение списка справочников или информации по конкретному справочнику"""
    collection = DictionaryNames()
    if code is None:
        # return list of Dictionaries
        try:
            result = collection.get_list()
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except ValueError, e:
            return jsonify(dict())
        return jsonify(data=list(result))
    else:
        # return Dictionary info by code
        result = collection.get_by_code(code)
        if result is None:
            raise InvalidAPIUsage(u'По коду {0} ничего не найдено'.format(code), status_code=404)
        return jsonify(result)


@module.route(base_url + 'find/', methods=['POST'])
@crossdomain('*', methods=['POST'])
def dictionaries_find():
    """Поиск информации о справочнике"""
    data = parse_request(request)
    obj = DictionaryNames()
    try:
        result = obj.get_list(data)
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except ValueError, e:
        return jsonify(dict())
    return jsonify(data=list(result))


@module.route(base_url, methods=['POST'])
@crossdomain('*', methods=['POST'])
def dictionaries_post():
    """Заведение информации о справочнике"""
    data = parse_request(request)
    obj = DictionaryNames()
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
def dictionaries_put(code):
    """Обновление информации о справочнике"""
    data = parse_request(request)
    obj = DictionaryNames()
    try:
        document = obj.get_by_code(code)
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    else:
        try:
            obj.update(_id=document.get('_id'), data=data)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except AttributeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
    return make_response(jsonify(), 200)


@module.route(base_url + '<code>/', methods=['DELETE'])
@crossdomain('*', methods=['DELETE'])
def dictionaries_delete(code):
    """Удаление справочника"""
    obj = DictionaryNames()
    try:
        obj.delete(code=code)
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except RuntimeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    return make_response(jsonify(), 204)
