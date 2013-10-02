# -*- encoding: utf-8 -*-
import logging
from ..connectors import db_local
from pymongo.errors import *
from config import MODULE_NAME

logger = logging.getLogger(MODULE_NAME)


class Collections(object):

    def get_list(self):
        return db_local.collection_names()


class Clients(object):

    def __init__(self):
        self.code = 'clients'
        self.dictionary = Dictionary(self.code)

    def get_list(self):
        return self.dictionary.get_list()

    def get_by_code(self, code):
        return self.dictionary.get_document(dict(code=code))

    def add(self, data):
        result = None
        if data is not None and isinstance(data, dict):
            if not self.dictionary.exists(data):
                self.dictionary.add_document(data)
        return result

    def update(self, _id, data):
        result = None
        if data is not None and isinstance(data, dict):
            result = self.dictionary.add_document(data.update(dict(_id=_id)))
        return result

    def delete(self, _id):
        return self.dictionary.delete(_id)


class DictionaryNames(object):

    def __init__(self):
        self.code = 'dict_names'
        self.dictionary = Dictionary(self.code)

    def get_list(self):
        return self.dictionary.get_list()

    def get_by_code(self, code):
        return self.dictionary.get_document(dict(code=code))

    def add(self, data):
        result = None
        if data is not None and isinstance(data, dict):
            if not self.dictionary.exists(data):
                self.dictionary.add_document(data)
        return result

    def update(self, _id, data):
        result = None
        if data is not None and isinstance(data, dict):
            result = self.dictionary.add_document(data.update(dict(_id=_id)))
        return result

    def delete(self, code):
        db_local.drop_collection()
        db_error = db_local.error()
        if db_error is not None:
            error = u'Возникла ошибка при удалении справочника {1} ({1})'.format(code, db_error)
            logger.error(error)
            raise RuntimeError(error)
        try:
            document = self.get_by_code(code)
        except TypeError, e:
            error = u'Некорректные входные параметры ({0})'.format(e)
            logger.error(error)
            raise TypeError(error)
        return self.dictionary.delete(document.get('_id'))


class Dictionary(object):

    def __init__(self, code):
        self.code = code
        self.collection = db_local[code]

    def add_document(self, data):
        if data is not None and isinstance(data, dict):
            _id = data.pop('_id', None)
            if _id is not None:
                try:
                    #TODO: use SONManipulator for ids in different clients?
                    result = self.collection.update({'_id': _id}, {'$set': data})
                except TypeError, e:
                    error = u'Некорректные входные параметры ({0})'.format(e)
                    logger.error(error)
                    raise TypeError(error)
            else:
                result = self.collection.insert(data)
        else:
            error = u'Некорректные входные параметры'
            logger.error(error)
            raise AttributeError(error)
        return result

    def add_documents(self, data=list()):
        result = None
        if data is not None:
            if isinstance(data, list):
                result = self.collection.insert(data)
            elif isinstance(data, dict):
                result = self.add_document(data)
        return result

    def get_document(self, find):
        try:
            result = self.collection.find_one(find)
        except TypeError, e:
            error = u'Неверный тип параметров ({0})'.format(e)
            logger.error(error)
            raise TypeError(error)
        return result

    def get_list(self, find=None):
        if find is not None and isinstance(find, dict):
            try:
                result = self.collection.find(find)
            except TypeError, e:
                error = u'Неверный тип параметров ({0})'.format(e)
                logger.error(error)
                raise TypeError(error)
        else:
            result = self.collection.find()
        return result

    def exists(self, find):
        try:
            result = self.collection.find(find).count()
        except TypeError, e:
            error = u'Неверный тип параметров ({0})'.format(e)
            logger.error(error)
            raise TypeError(error)
        return bool(result)

    def delete(self, _id):
        if not _id:
            return False
        try:
            self.collection.remove(_id)
        except TypeError, e:
            error = u'Неверный тип параметров ({0})'.format(e)
            logger.error(error)
            raise TypeError(error)
        except OperationFailure, e:
            error = u'Операция удаления документа с id={0} не выполнена ({1})'.format(_id, e)
            logger.error(error)
            raise RuntimeError(error)
        return True