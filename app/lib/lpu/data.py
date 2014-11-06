# -*- coding: utf-8 -*-
from sqlalchemy import MetaData
from datetime import datetime, timedelta, date
from bson import Binary
from ..data import DictionaryNames, Dictionary
from app.lib.utils.tools import logger
from .db import connection, db_disconnect, engine


class LPU_Data:

    def __init__(self):
        self.msg = list()

    def __get_local_dictionary(self, code):
        obj = DictionaryNames()
        return obj.get_by_code(code)

    def __add_dictionary(self, code, name=None):
        obj = DictionaryNames()
        self.msg.append(u'Локальный справочник ({0}) не существует, создаём его'.format(code))
        data = dict(code=code)
        if name:
            data.update({'name': name})
        return obj.add(data)

    def __prepare_document(self, row, table):
        dictionary = dict()
        for key, value in row.items():
            if 'BLOB' in str(table.columns[key].type):
                value = Binary(value)
            elif isinstance(value, str) or isinstance(value, unicode):
                value = value.strip()
            elif isinstance(value, timedelta):
                value = (datetime.min + value).time().isoformat()
            elif isinstance(value, date):
                value = datetime.combine(value, datetime.min.time())
            dictionary[key] = value
        return dictionary

    def __doc_info(self, document):
        return u', '.join([u'{0}: {1}'.format(key, value) for key, value in document.iteritems()])

    def __add_data(self, table, data):
        code = table.name
        obj = Dictionary(code)
        for row in data:
            document = self.__prepare_document(row, table)
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

    def get_rb_names(self):
        meta = MetaData(engine)
        meta.reflect(bind=engine, views=True,
                     only=lambda name, obj: name.startswith(u'MKB') or name.startswith(u'rb') and not name.startswith(u'rb_'))

        return meta.tables

    def import_lpu_dictionaries(self, dictionaries, clear=False):
        for name, table in dictionaries.iteritems():
            if not name.startswith(u'rb') and not name.startswith(u'MKB') or name.startswith(u'rb_'):
                continue
            self.msg = list()
            data = self.__get_data(name)
            if clear:
                self.__clear_data(name)
            if data:
                result = self.__add_data(table, data)
                data.close()
            logger.debug(u'\n'.join(self.msg), extra=dict(tags=['lpu', 'import', name]))
        db_disconnect()

    def import_risar_dictionaries(self, clear=False):
        risar_rbs = connection.execute(
            'SELECT code, name, valueDomain '
            'FROM hospital1.ActionPropertyType '
            'WHERE actionType_id = 4515  and deleted = 0 and valueDomain != "";')
        for row in risar_rbs:
            code = u'rbRisar{0}'.format(row['code'].title())
            name = row['name']
            values = [{'name': val.strip("'").strip()} for val in row['valueDomain'].split(',')]
            local_dictionary = self.__get_local_dictionary(code)
            if clear:
                self.__clear_data(code)
            if not local_dictionary:
                self.__add_dictionary(code, name)
            obj = Dictionary(code)
            for document in values:
                try:
                    result = obj.add_document(document)
                except AttributeError, e:
                    logger.error(
                        self.msg.append(u'Ошибка импорта документа ({0}): {1}'.format(self.__doc_info(document), e)),
                        extra=dict(tags=['lpu', 'import error']))
                    return False
            self.msg.append(u'Справочник ({0}) обновлён'.format(code))
        logger.debug(u'\n'.join(self.msg), extra=dict(tags=['risar', 'import']))
        db_disconnect()