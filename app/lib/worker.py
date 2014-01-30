# -*- encoding: utf-8 -*-
import re
from app.lib.utils.tools import logger
from .data import Dictionary, DictionaryNames, Collections


class Worker:

    def __init__(self, code):
        self.code = code
        self.collection = Dictionary(code)

    def __link_document(self, document, data):
        pass

    def __prepare_value(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            value = value.replace('.', '')
            value = re.compile(value, re.IGNORECASE)
        return value

    def __get_linked_data(self, code, field, value):
        collection = Dictionary(code)
        document = collection.get_document({field: self.__prepare_value(value)})
        return document

    def __link_documents(self, collection_code, origin_field, linked_field):
        for document in self.collection.get_list():
            if origin_field in document:
                linked_document = self.__get_linked_data(collection_code, linked_field, document[origin_field])
                if linked_document:
                    document.update({collection_code: linked_document})
                    self.collection.add_document(document)

    def link_collection(self, collection_code, origin_field, linked_field):
        dict_name = DictionaryNames()
        origin_collection = dict_name.get_by_code(self.code)
        linked_collection = dict_name.get_by_code(collection_code)
        if not origin_collection:
            logger.error(u'Не найден документ ({0}) в dict_names'.format(self.code), extra=dict(tags=['worker']))
            return False
        if not linked_collection:
            logger.error(u'Не найден привязываемая коллекция ({0}) в dict_names'.format(collection_code),
                         extra=dict(tags=['worker']))
            return False
        version = linked_collection.pop('version')
        origin_collection.update({'linked': {'collection': linked_collection,
                                             'origin_field': origin_field,
                                             'linked_field': linked_field}})
        dict_name.update(origin_collection.pop('_id'), origin_collection)

        if origin_field and linked_field:
            self.__link_documents(collection_code, origin_field, linked_field)