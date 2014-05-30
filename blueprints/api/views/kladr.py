# -*- coding: utf-8 -*-
from app.lib.utils.tools import prepare_find_params
from app.lib.utils.exceptions import InvalidAPIUsage
from app.lib.data import Dictionary
from app.lib.utils.tools import jsonify, crossdomain
from ..app import module

CITY_CODE = 'KLD172'
STREET_CODE = 'STR172'


@module.route('/kladr/city/<value>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
def get_city(value):
    obj = Dictionary(CITY_CODE)
    find = {'is_actual': '1',
            '$or': [{'name': prepare_find_params(value)},
                    {'identcode': value}]}
    try:
        result = obj.get_list(find, 'level')
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    return jsonify(data=list(result))


@module.route('/kladr/street/<city_code>/<value>/', methods=['GET'])
@crossdomain('*', methods=['GET'])
def get_street(city_code, value):
    obj = Dictionary(STREET_CODE)
    find = {'identparent': city_code,
            'is_actual': '1',
            '$or': [{'name': prepare_find_params(value)},
                    {'identcode': value}]}
    try:
        result = obj.get_list(find)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    return jsonify(data=list(result))