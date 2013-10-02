# -*- encoding: utf-8 -*-
import logging
from ..connectors import db_local
from pymongo.errors import *
from pymongo.collection import Collection
from config import MODULE_NAME

logger = logging.getLogger(MODULE_NAME)


class Collections(object):

    def get_list(self):
        return db_local.collection_names()


class DictionaryNames(object):

    def __init__(self):
        self.code = 'dict_names'
        self.dictionary = Dictionary(self.code)

    def get_list(self):
        return self.dictionary.get_list()

    def add(self, data):
        if data is not None and isinstance(data, dict):
            if not self.dictionary.exists(data):
                self.dictionary.add_document(data)


class Clients(object):

    def __init__(self):
        self.code = 'clients'
        self.dictionary = Dictionary(self.code)

    def get_list(self):
        return self.dictionary.get_list()

    def add(self, data):
        if data is not None and isinstance(data, dict):
            if not self.dictionary.exists(data):
                self.dictionary.add_document(data)


class Dictionary(object):

    def __init__(self, code):
        self.code = code
        self.collection = db_local[code]

    def add_document(self, data):
        if data is not None and isinstance(data, dict):
            _id = data.pop('_id', None)
            if _id is not None:
                self.collection.update({'_id': _id}, {'$set': data})
            else:
                self.collection.insert(data)

    def add_documents(self, data=list()):
        if data is not None:
            if isinstance(data, list):
                self.collection.insert(data)
            elif isinstance(data, dict):
                self.add_document(data)

    def get_list(self, find=None):
        if find is None and isinstance(find, dict):
            try:
                result = self.collection.find(find)
            except TypeError, e:
                logger.error(u'Неверный тип параметров ({0})'.format(e))
                return None
        else:
            result = self.collection.find()
        return result

    def exists(self, find):
        try:
            result = self.collection.find(find).count()
        except TypeError, e:
            logger.error(u'Неверный тип параметров ({0})'.format(e))
            return None
        return bool(result)

    def delete(self, _id):
        if not _id:
            return False
        try:
            self.collection.remove(_id)
        except OperationFailure, e:
            logger.error(u'Операция удаления документа с id={0} не выполнена ({1})'.format(_id, e))
            return False
        return True