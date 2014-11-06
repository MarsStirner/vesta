# -*- coding: utf-8 -*-
from flask import make_response
from app.lib.utils.exceptions import InvalidAPIUsage
from app.lib.data import Clients, DictionaryNames, Dictionary
from app.lib.utils.tools import jsonify
from bson.objectid import InvalidId
from ..app import module


def get_linked_dict(document, collection):
    # Если в документе задана привязка к справочнику - используем её
    if document and 'linked_collection' in document:
        obj_names = DictionaryNames()
        linked_dict = obj_names.get_by_code(document['linked_collection'])
        return linked_dict

    # Иначе смотрим на привязку самого справочника
    try:
        linked_dict = collection['linked']['collection']
    except AttributeError:
        raise InvalidAPIUsage(u'Not found', status_code=404)
    except KeyError:
        raise InvalidAPIUsage(u'Not found', status_code=404)
    else:
        return linked_dict


@module.route('/<code>/<field>/<field_value>/', methods=['GET'])
def get_linked_data(code, field, field_value):
    # TODO: try-except
    obj = Dictionary(code)
    obj_names = DictionaryNames()
    document = obj.get_document({str(field): field_value})
    try:
        origin_dict = obj_names.get_by_code(code)
        try:
            linked_dict = get_linked_dict(document, origin_dict)
        except AttributeError:
            raise InvalidAPIUsage(u'Not found', status_code=404)
        except KeyError:
            raise InvalidAPIUsage(u'Not found', status_code=404)
        if not document:
            return make_response(jsonify(dict(oid=linked_dict['oid'], data={})), 200)
    except TypeError, e:
        raise InvalidAPIUsage(e.message, status_code=400)
    except InvalidId, e:
        raise InvalidAPIUsage(e.message, status_code=404)
    return make_response(jsonify(dict(oid=linked_dict['oid'], data=document[linked_dict['code']])), 200)
