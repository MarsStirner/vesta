# -*- coding: utf-8 -*-
from sqlalchemy.sql import text
from datetime import datetime
from ..data import DictionaryNames, Dictionary
from app.lib.utils.tools import logger
from .db import connection, db_disconnect


class LPU_Data:

    def __init__(self):
        self.msg = list()

    def __get_local_dictionary(self, code):
        obj = DictionaryNames()
        return obj.get_by_code(code)

    def __add_dictionary(self, code):
        obj = DictionaryNames()
        self.msg.append(u'Локальный справочник ({0}) не существует, создаём его'.format(code))
        return obj.add(dict(code=code))

    def __prepare_document(self, row):
        dictionary = dict()
        for key, value in row.items():
            if isinstance(value, str) or isinstance(value, unicode):
                value = value.strip()
            dictionary[key] = value
        return dictionary

    def __doc_info(self, document):
        return u', '.join([u'{0}: {1}'.format(key, value) for key, value in document.iteritems()])

    def __add_data(self, code, data):
        obj = Dictionary(code)
        for row in data:
            document = self.__prepare_document(row)
            existdocument = None
            if not document:
                continue
            if 'id' in document:
                existdocument = obj.get_document(dict(id=document['id']))
            if existdocument:
                document.update(dict(_id=existdocument['_id']))
            # self.msg.append(u'Обновляем документ ({0})'.format(self.__doc_info(document)))
            try:
                result = obj.add_document(document)
            except AttributeError, e:
                logger.error(
                    self.msg.append(u'Ошибка импорта документа ({0}): {1}'.format(self.__doc_info(document), e)),
                    extra=dict(tags=['lpu', 'import error']))
                return False
            # else:
            #     self.msg.append(u'{0}'.format(result))
        self.msg.append(u'Справочник ({0}) обновлён'.format(code))
        return True

    def __get_data(self, code):
        local_dictionary = self.__get_local_dictionary(code)
        if not local_dictionary:
            self.__add_dictionary(code)
        result = connection.execute('SELECT * FROM {0} WHERE 1 ORDER BY id'.format(code))
        return result

    def __clear_data(self, code):
        obj = Dictionary(code)
        obj.remove()

    def import_lpu_dictionaries(self, dictionaries, clear=False):
        for code in dictionaries:
            self.msg = list()
            data = self.__get_data(code)
            if clear:
                self.__clear_data(code)
            if data:
                result = self.__add_data(code, data)
                data.close()
            logger.debug(u'\n'.join(self.msg), extra=dict(tags=['lpu', 'import', code]))
        db_disconnect()