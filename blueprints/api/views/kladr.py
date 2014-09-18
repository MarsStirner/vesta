# -*- coding: utf-8 -*-
from app.lib.utils.tools import prepare_find_params
from app.app import cache
from app.lib.utils.exceptions import InvalidAPIUsage
from app.lib.data import Dictionary
from app.lib.utils.tools import jsonify, crossdomain
from ..app import module

CITY_CODE = 'KLD172'
STREET_CODE = 'STR172'


@module.route('/kladr/city/search/<value>/', methods=['GET'])
@module.route('/kladr/city/search/<value>/<int:limit>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
@cache.memoize(86400)
def search_city(value, limit=None):
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
        result = _set_cities_parents(cities)
    return jsonify(data=list(result))


@module.route('/kladr/psg/search/<value>/', methods=['GET'])
@module.route('/kladr/psg/search/<value>/<int:limit>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
@cache.memoize(86400)
def search_city_country(value, limit=None):
    obj = Dictionary(CITY_CODE)
    find = {'is_actual': '1',
            'shorttype': {'$in': [u'г', u'с', u'п']},
            '$or': [{'name': prepare_find_params(value)},
                    {'identcode': value}]}
    try:
        cities = obj.get_list(find, 'level', limit)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    else:
        result = _set_cities_parents(cities)
    return jsonify(data=list(result))


@module.route('/kladr/street/search/<city_code>/<value>/', methods=['GET'])
@module.route('/kladr/street/search/<city_code>/<value>/<int:limit>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
@cache.memoize(86400)
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
@cache.memoize(86400)
def get_city(code):
    obj = Dictionary(CITY_CODE)
    find = {'identcode': code}
    try:
        cities = obj.get_list(find)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    else:
        result = _set_cities_parents(cities)
    return jsonify(data=list(result))


@module.route('/kladr/street/<code>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
@cache.memoize(86400)
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


def _set_cities_parents(cities):
    obj = Dictionary(CITY_CODE)
    result = []
    for city in cities:
        city['parents'] = []
        identparent = city['identparent']
        parent = city.get('parent')
        if identparent or parent:
            level = int(city['level'])
            for i in xrange(level - 1, 0, -1):
                if parent:
                    parent_city = obj.get_document({'_id': parent})
                elif identparent:
                    parent_city = obj.get_document({'identcode': identparent})
                else:
                    break
                city['parents'].append(parent_city)
                parent = parent_city.get('parent')
                identparent = parent_city['identparent']
        result.append(city)
    return result