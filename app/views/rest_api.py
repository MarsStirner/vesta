# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import g, make_response, abort, request
from app.app import app
from utils.logs.exceptions import InvalidAPIUsage
from ..lib.data import Clients, DictionaryNames, Dictionary
from utils.tools import jsonify as vesta_jsonify, json
from bson.objectid import ObjectId, InvalidId


def user_required(f):
    """Checks whether user is logged in or raises error 401."""
    def decorator(*args, **kwargs):
        if not g.user:
            raise InvalidAPIUsage(u'Необходимо авторизовать клиента', status_code=401)
        return f(*args, **kwargs)
    return decorator


class APIMixin(object):
    def parse_request(self, _request):
        data = _request.json
        if not data:
            data = json.loads(_request.data)
        if not data:
            raise InvalidAPIUsage(u'Не переданы данные, или переданы неверным методом', 400)
        return data


class ClientsAPI(MethodView, APIMixin):
    """API для работы с информацией о зарегистрированных клиентах (внешних системах)"""
    #decorators = [user_required]

    def get(self, code):
        """Получение списка клиентов или информации по конкретному клиенту"""
        collection = Clients()
        if code is None:
            # return list of Clients
            try:
                result = collection.get_list()
            except TypeError, e:
                raise InvalidAPIUsage(e.message, status_code=400)
            except ValueError, e:
                return vesta_jsonify(dict())
            return vesta_jsonify(dict(result=list(result)))
        else:
            # return Dictionary info by code
            result = collection.get_by_code(code)
            if result is None:
                result = dict()
            return vesta_jsonify(result)

    def post(self):
        """Заведение информации о клиенте"""
        data = self.parse_request(request)
        obj = Clients()
        try:
            _id = obj.add(data)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except AttributeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        else:
            if _id:
                return make_response(vesta_jsonify(dict(_id=str(_id))), 201)
            raise InvalidAPIUsage(u'Ошибка добавления данных', 500)

    def put(self, code):
        """Обновление информации о клиенте"""
        data = self.parse_request(request)
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
        return make_response(vesta_jsonify(dict(_id=_id)), 200)

    def delete(self, code):
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
        return make_response(vesta_jsonify(), 204)

    @classmethod
    def register(cls, mod):
        url = '/clients/'
        f = cls.as_view('clients_api')
        mod.add_url_rule(url, view_func=f, methods=['GET'], defaults={"code": None})
        mod.add_url_rule(url, view_func=f, methods=['POST'])
        mod.add_url_rule('{0}<string:code>/'.format(url), view_func=f, methods=['GET', 'PUT', 'DELETE'])


class DictionaryNamesAPI(MethodView, APIMixin):
    """API для работы с информацией о справочниках"""
    #decorators = [user_required]

    def get(self, code):
        """Получение списка справочников или информации по конкретному справочнику"""
        collection = DictionaryNames()
        if code is None:
            # return list of Dictionaries
            try:
                result = collection.get_list()
            except TypeError, e:
                raise InvalidAPIUsage(e.message, status_code=400)
            except ValueError, e:
                return vesta_jsonify(dict())
            return vesta_jsonify(result=list(result))
        else:
            # return Dictionary info by code
            result = collection.get_by_code(code)
            if result is None:
                result = dict()
            return vesta_jsonify(result)

    def post(self):
        """Заведение информации о справочнике"""
        data = self.parse_request(request)
        obj = DictionaryNames()
        try:
            _id = obj.add(data)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except AttributeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        else:
            if _id:
                return make_response(vesta_jsonify(dict(_id=str(_id))), 201)
            raise InvalidAPIUsage(u'Ошибка добавления данных', 500)

    def put(self, code):
        """Обновление информации о справочнике"""
        data = self.parse_request(request)
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
        return make_response(vesta_jsonify(), 200)

    def delete(self, code):
        """Удаление справочника"""
        obj = DictionaryNames()
        try:
            obj.delete(code=code)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except RuntimeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        return make_response(vesta_jsonify(), 204)

    @classmethod
    def register(cls, mod):
        url = '/dictionaries/'
        f = cls.as_view('dictionaries_api')
        mod.add_url_rule(url, view_func=f, methods=['GET'], defaults={"code": None})
        mod.add_url_rule(url, view_func=f, methods=['POST'])
        mod.add_url_rule('{0}<string:code>/'.format(url), view_func=f, methods=['GET', 'PUT', 'DELETE'])


class DictionaryAPI(MethodView, APIMixin):
    """API для работы с конкретным справочником"""
    #decorators = [user_required]

    def get(self, code, document_id):
        if document_id is None:
            return self.list_documents(code)
        else:
            result = self.document_details(code, document_id)
            if not result:
                abort(404)
            return vesta_jsonify(result)

    def list_documents(self, code, find=None):
        obj = Dictionary(code)
        try:
            result = obj.get_list(find)
        except ValueError, e:
            raise InvalidAPIUsage(e.message, status_code=404)
        except AttributeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        return vesta_jsonify(result)

    def post(self, code):
        data = self.parse_request(request)
        obj = Dictionary(code)
        try:
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
                return make_response(vesta_jsonify(dict(_id=_id)), 201)
            raise InvalidAPIUsage(u'Ошибка добавления данных', 500)

    def document_details(self, code, document_id):
        obj = Dictionary(code)
        #TODO: учесть auth_token
        try:
            result = obj.get_document(dict(_id=ObjectId(document_id)))
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except InvalidId, e:
            raise InvalidAPIUsage(e.message, status_code=404)
        return result

    def put(self, code, document_id):
        data = self.parse_request(request)
        obj = Dictionary(code)
        try:
            exists = obj.exists(dict(_id=ObjectId(document_id)))
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        try:
            data.update(dict(_id=ObjectId(document_id)))
            result = obj.add_document(data)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except AttributeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        if not exists:
            return make_response(vesta_jsonify(dict(_id=result)), 201)
        return make_response(vesta_jsonify(), 200)

    def delete(self, code, document_id):
        obj = Dictionary(code)
        try:
            obj.delete(_id=ObjectId(document_id))
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except RuntimeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        return make_response(vesta_jsonify(), 204)

    @classmethod
    def register(cls, mod):
        url = '/dictionary/<string:code>/'
        f = cls.as_view('dictionary_api')
        mod.add_url_rule(url, view_func=f, methods=['GET'], defaults={'document_id': None})
        mod.add_url_rule(url, view_func=f, methods=['POST'])
        mod.add_url_rule('{0}<string:document_id>/'.format(url), view_func=f, methods=['GET', 'PUT', 'DELETE'])

ClientsAPI.register(app)
DictionaryNamesAPI.register(app)
DictionaryAPI.register(app)