# -*- coding: utf-8 -*-
from app.lib.utils.tools import prepare_find_params
from app.app import cache
from app.lib.utils.exceptions import InvalidAPIUsage
from app.lib.data import Dictionary
from app.lib.utils.tools import jsonify, crossdomain
from ..app import module


CLASS_CODE = 'rbPspdDocumentClass'
TYPE_CODE = 'rbPspdDocumentType'
FIELD_CODE = 'rbPspdDocumentField'


@module.route('/v1/{0}/'.format(CLASS_CODE), methods=['GET'])
@module.route('/v1/{0}/<field>/<value>/'.format(CLASS_CODE), methods=['GET'])
@crossdomain('*', methods=['GET'])
@cache.memoize(86400)
def search_class(field=None, value=None):
    obj = Dictionary(CLASS_CODE)
    find = None
    if field and value:
        find = {field: prepare_find_params(value)}
    try:
        classes = obj.get_list(find)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    else:
        result = _set_types(classes)
    return jsonify(data=list(result))


@module.route('/v1/{0}/'.format(TYPE_CODE), methods=['GET'])
@module.route('/v1/{0}/<field>/<value>/'.format(TYPE_CODE), methods=['GET'])
@crossdomain('*', methods=['GET'])
@cache.memoize(86400)
def search_type(field=None, value=None):
    obj = Dictionary(TYPE_CODE)
    find = None
    if field and value:
        find = {field: prepare_find_params(value)}
    try:
        types = obj.get_list(find)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    else:
        result = _set_fields(types)
    return jsonify(data=list(result))


@module.route('/v1/{0}/'.format(FIELD_CODE), methods=['GET'])
@module.route('/v1/{0}/<field>/<value>/'.format(FIELD_CODE), methods=['GET'])
@crossdomain('*', methods=['GET'])
@cache.memoize(86400)
def search_fields(field=None, value=None):
    obj = Dictionary(FIELD_CODE)
    find = None
    if field and value:
        find = {field: prepare_find_params(value)}
    try:
        result = obj.get_list(find)
    except ValueError, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    except AttributeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    return jsonify(data=list(result))


def _set_types(classes):
    result = []
    obj = Dictionary(TYPE_CODE)
    for _class in classes:
        _class['types'] = []
        for _type in obj.get_list({'class_code': _class['code']}):
            _class['types'].append(_set_fields([_type]))
        result.append(_class)
    return result


def _set_fields(types):
    result = []
    obj = Dictionary(FIELD_CODE)
    for _type in types:
        _type['fields'] = list(obj.get_list({'type_code': _type['code']}))
        result.append(_type)
    return result
