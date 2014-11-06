# -*- coding: utf-8 -*-
from flask import make_response, request
from app.lib.utils.exceptions import InvalidAPIUsage
from app.lib.data import Clients, DictionaryNames, Dictionary
from app.lib.utils.tools import jsonify, json, prepare_find_params, parse_request
from bson.objectid import InvalidId
from ..app import module
from nsi import get_linked_dict

nsi_name_keys = ('name', 'name_short', 'descr', 'res_descr', 'mkb_name')


def _prepare_hs_response(data, dict_code):
    return_data = dict()
    if 'unq' in data:
        return_data['code'] = data['unq']
    elif 'mkb_code' in data:
        return_data['code'] = data['mkb_code']
    elif 'code' in data:
        return_data['code'] = data['code']
    elif 'id' in data:
        return_data['code'] = data['id']
    elif 'recid' in data:
        return_data['code'] = data['recid']

    for key in nsi_name_keys:
        if key in data:
            return_data['name'] = data[key]
            break

    # Для rbSocStatusType и MDN366 в поле code проставляется значение из id
    if dict_code in ('rbSocStatusType', 'MDN366'):
        return_data['code'] = data['id']
    return return_data


@module.route('/hs/<code>/<field>/<field_value>/', methods=['GET'])
def get_data_hs(code, field, field_value):
    # TODO: try-except
    obj = Dictionary(code)
    obj_names = DictionaryNames()
    document = obj.get_document({str(field): field_value})
    origin_dict = obj_names.get_by_code(code)
    if 'oid' in origin_dict:
        # Работаем с НСИ справочником
        data = document
        oid = origin_dict['oid']
    else:
        try:
            try:
                linked_dict = get_linked_dict(document, origin_dict)
            except AttributeError:
                raise InvalidAPIUsage(u'Not found', status_code=404)
            except KeyError:
                raise InvalidAPIUsage(u'Not found', status_code=404)
            if not document:
                return make_response(jsonify(dict(oid=linked_dict['oid'], message="not found")), 404)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except InvalidId, e:
            raise InvalidAPIUsage(e.message, status_code=404)
        data = document.get(linked_dict['code'])
        oid = linked_dict['oid']
    if data:
        data = _prepare_hs_response(data, code)
    else:
        data = dict()
    return make_response(jsonify(dict(oid=oid, data=data)), 200)


@module.route('/hs/<code>/', methods=['POST'])
def find_data_hs(code):
    data = parse_request(request)
    obj = Dictionary(code)
    obj_names = DictionaryNames()
    try:
        _dict = obj_names.get_by_code(code)
        result = obj.get_document(prepare_find_params(data))
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