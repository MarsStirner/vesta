# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import jsonify, g, make_response
from app import app
from utils.logs.exceptions import InvalidAPIUsage
from ..lib.data import Clients, DictionaryNames, Dictionary


def user_required(f):
    """Checks whether user is logged in or raises error 401."""
    def decorator(*args, **kwargs):
        if not g.user:
            raise InvalidAPIUsage(u'Необходимо авторизовать клиента', status_code=401)
        return f(*args, **kwargs)
    return decorator


class ClientsAPI(MethodView):
    """API для работы с информацией о зарегистрированных клиентах (внешних системах)"""
    decorators = [user_required]

    def get(self, code):
        """Получение списка клиентов или информации по конкретному клиенту"""
        collection = DictionaryNames()
        if code is None:
            # return list of Clients
            try:
                result = collection.get_list()
            except TypeError, e:
                raise InvalidAPIUsage(e.message, status_code=400)
            return jsonify(result)
        else:
            # return Dictionary info by code
            return jsonify(collection.get_by_code(code))

    def post(self, data):
        """Заведение информации о клиенте"""
        obj = DictionaryNames()
        try:
            result = obj.add(data)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except AttributeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        else:
            return make_response(jsonify(result), 201)

    def put(self, code, data):
        """Обновление информации о клиенте"""
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
        return make_response(200)

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
        return make_response(204)

    @classmethod
    def register(cls, mod):
        url = '/clients/'
        f = cls.as_view('clients_api')
        mod.add_url_rule(url, view_func=f, methods=['GET'], defaults={"code": None})
        mod.add_url_rule(url, view_func=f, methods=['POST'])
        mod.add_url_rule('{0}<regex("[\w]*[Ss]"):code>'.format(url), view_func=f, methods=['GET', 'PUT', 'DELETE'])


class DictionaryNamesAPI(MethodView):
    """API для работы с информацией о справочниках"""
    decorators = [user_required]

    def get(self, code):
        """Получение списка справочников или информации по конкретному справочнику"""
        collection = DictionaryNames()
        if code is None:
            # return list of Dictionaries
            try:
                result = collection.get_list()
            except TypeError, e:
                raise InvalidAPIUsage(e.message, status_code=400)
            return jsonify(result)
        else:
            # return Dictionary info by code
            return jsonify(collection.get_by_code(code))

    def post(self, data):
        """Заведение информации о справочнике"""
        obj = DictionaryNames()
        try:
            result = obj.add(data)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except AttributeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        else:
            return make_response(jsonify(result), 201)

    def put(self, code, data):
        """Обновление информации о справочнике"""
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
        return make_response(200)

    def delete(self, code):
        """Удаление справочника"""
        obj = DictionaryNames()
        try:
            obj.delete(code=code)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except RuntimeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        return make_response(204)

    @classmethod
    def register(cls, mod):
        url = '/dictionaries/'
        f = cls.as_view('dictionaries_api')
        mod.add_url_rule(url, view_func=f, methods=['GET'], defaults={"code": None})
        mod.add_url_rule(url, view_func=f, methods=['POST'])
        mod.add_url_rule('{0}<regex("[\w]*[Ss]"):code>'.format(url), view_func=f, methods=['GET', 'PUT', 'DELETE'])


class DictionaryAPI(MethodView):
    """API для работы с конкретным справочником"""
    decorators = [user_required]

    def get(self, code, document_id):
        if document_id is None:
            return self.list_documents(code)
        else:
            result = self.document_details(code, document_id)
            if not result:
                return make_response(404)
            return jsonify(result)

    def list_documents(self, code, find=None):
        obj = Dictionary(code)
        try:
            result = obj.get_list(find)
        except AttributeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        return jsonify(result)

    def post(self, code, data):
        obj = Dictionary(code)
        try:
            result = obj.add_documents(data)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except AttributeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        else:
            return make_response(jsonify(result), 201)

    def document_details(self, code, document_id):
        obj = Dictionary(code)
        #TODO: учесть auth_token
        try:
            result = obj.get_document(dict(_id=document_id))
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        return result

    def put(self, code, document_id, data):
        obj = Dictionary(code)
        try:
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
            return make_response(jsonify(result), 201)
        return make_response(200)

    def delete(self, code, document_id):
        obj = Dictionary(code)
        try:
            obj.delete(_id=document_id)
        except TypeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        except RuntimeError, e:
            raise InvalidAPIUsage(e.message, status_code=400)
        return make_response(204)

    @classmethod
    def register(cls, mod):
        url = '/dictionary/<string:code>/'
        f = cls.as_view('dictionary_api')
        mod.add_url_rule(url, view_func=f, methods=['GET'], defaults={'document_id': None})
        mod.add_url_rule(url, view_func=f, methods=['POST'])
        mod.add_url_rule('{0}<int:document_id>'.format(url), view_func=f, methods=['GET', 'PUT', 'DELETE'])

ClientsAPI.register(app)
DictionaryNamesAPI.register(app)
DictionaryAPI.register(app)