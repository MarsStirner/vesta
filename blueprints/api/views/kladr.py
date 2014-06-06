# -*- coding: utf-8 -*-
from app.lib.utils.tools import prepare_find_params
from app.lib.utils.exceptions import InvalidAPIUsage
from app.lib.data import Dictionary
from app.lib.utils.tools import jsonify, crossdomain
from ..app import module

CITY_CODE = 'KLD172'
STREET_CODE = 'STR172'


@module.route('/kladr/city/search/<value>/', methods=['GET'])
@module.route('/kladr/city/search/<value>/<int:limit>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
def search_city(value, limit=None):
    result = list()
    obj = Dictionary(CITY_CODE)
    find = {'is_actual': '1',
            '$or': [{'name': prepare_find_params(value)},
                    {'identcode': value}]}
    try:
        cities = obj.get_list(find, 'level', limit)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    else:
        for city in cities:
            city['parents'] = []
            if city['identparent']:
                # TODO: заменить ['identparent'] на ['parent']
                identparent = city['identparent']
                level = int(city['level'])
                for i in xrange(level - 1, 0, -1):
                    if not identparent:
                        break
                    parent = obj.get_document({'identcode': identparent})
                    city['parents'].append(parent)
                    identparent = parent['identparent']
            result.append(city)
    return jsonify(data=list(result))


@module.route('/kladr/street/search/<city_code>/<value>/', methods=['GET'])
@module.route('/kladr/street/search/<city_code>/<value>/<int:limit>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
def search_street(city_code, value, limit=None):
    obj = Dictionary(STREET_CODE)
    find = {'identparent': city_code,
            'is_actual': '1',
            '$or': [{'name': prepare_find_params(value)},
                    {'identcode': value}]}
    try:
        result = obj.get_list(find, limit=limit)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    return jsonify(data=list(result))


@module.route('/kladr/city/<code>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
def get_city(code):
    obj = Dictionary(CITY_CODE)
    find = {'identcode': code}
    try:
        result = obj.get_list(find)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    return jsonify(data=list(result))


@module.route('/kladr/street/<code>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
def get_street(code):
    obj = Dictionary(STREET_CODE)
    find = {'identcode': code}
    try:
        result = obj.get_list(find)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    return jsonify(data=list(result))