# -*- coding: utf-8 -*-
from datetime import datetime
from config import NSI_SOAP, NSI_TOKEN, DEBUG
from client import NSI_Client
from ..data import DictionaryNames, Dictionary
from app.lib.utils.tools import logger


class NSI_Data:

    def __init__(self):
        self.msg = list()
        self.client = NSI_Client(url=NSI_SOAP, user_key=NSI_TOKEN)

    def __get_dictionaries(self):
        result = self.client.getRefbookList()
        return result

    def __get_dictionary(self, code, version):
        result = self.client.get_refbook_data(code, version)
        return result

    def __get_local_dictionary(self, code):
        obj = DictionaryNames()
        return obj.get_by_code(code)

    def __get_dictionary_versions(self, code):
        result = self.client.getVersionList(code)
        return result

    def __format_key(self, _key):
        _key = _key.lower()
        prefixes = ['s_', 'n_', 'v_']
        for prefix in prefixes:
            if _key.find(prefix) == 0:
                _key = _key.replace(prefix, '')
        return str(_key)

    def __prepare_dictionary(self, data):
        dictionary = dict()
        children = getattr(data, 'children', None)
        if children:
            for field in getattr(children, 'item', []):
                _key = self.__format_key(field.key)
                dictionary[_key] = field.value
        return dictionary

    def __get_data(self, dictionary, version, overwrite=False):
        obj = DictionaryNames()
        data = dict()
        local_dictionary = self.__get_local_dictionary(dictionary['code'])
        self.msg.append(u'Импорт {0} ({1})'.format(dictionary['name'], dictionary['code']))
        if local_dictionary and overwrite is False:
            if 'version' in local_dictionary:
                local_version = local_dictionary['version']
                if local_version['version'] != version['version']:
                    self.msg.append(u'Локальная версия справочника: {0}'.format(local_version))
                    self.msg.append(u'Актуальная версия справочника: {0}'.format(version))
                    self.msg.append(u'Версии не совпадают, обновляем diff')
                    data = self.client.getRefbookUpdate(code=dictionary['code'], user_version=local_version['version'])
            else:
                self.msg.append(u'Локальная версия справочника не задана, импортируем данные')
                obj.update(_id=local_dictionary['_id'], data=dictionary)
                data = self.__get_dictionary(dictionary['code'], version['version'])
        else:
            if overwrite:
                self.msg.append(u'Перезаписываем локальный справочник')
            else:
                self.msg.append(u'Локальный справочник не существует, импортируем данные')
            _id = obj.add(dictionary)
            data = self.__get_dictionary(dictionary['code'], version['version'])
        return data

    def __doc_info(self, document):
        return u', '.join([u'{0}: {1}'.format(key, value) for key, value in document.iteritems()])

    def __add_data(self, code, data):
        for document_data in data:
            if not document_data:
                continue
            result = self.__add_document(code, document_data)
            if result is False:
                return False
            # else:
            #     self.msg.append(u'{0}'.format(result))
        self.msg.append(u'Справочник ({0}) обновлён'.format(code))
        return True

    def __add_document(self, code, data):
        obj = Dictionary(code)
        document = self.__prepare_dictionary(data)
        exist_document = None
        if not document:
            return False
        if 'code' in document:
            exist_document = obj.get_document(dict(code=document['code']))
        elif 'id' in document:
            exist_document = obj.get_document(dict(id=document['id']))
        if exist_document:
            document.update(dict(_id=exist_document['_id']))
        # self.msg.append(u'Обновляем документ ({0})'.format(self.__doc_info(document)))
        try:
            result = obj.add_document(document)
        except AttributeError, e:
            logger.error(u'Ошибка импорта документа ({0}): {1}'.format(self.__doc_info(document), e),
                         extra=dict(tags=['nsi', 'import error']))
            return False
        else:
            return result

    def __add_parts_data(self, code, version):
        parts_number = self.client.get_parts_number(code, version)
        if parts_number:
            for i in xrange(1, parts_number + 1):
                data = self.client.get_parts_data(code, version, i)
                for document in data:
                    result = self.__add_document(code, document)
                    if result is False:
                        return False
        return True

    def __add_dict_data(self, dictionary, version, overwrite=False):
        obj = DictionaryNames()
        data = dict()
        local_dictionary = self.__get_local_dictionary(dictionary['code'])
        self.msg.append(u'Импорт {0} ({1})'.format(dictionary['name'], dictionary['code']))
        if local_dictionary and overwrite is False:
            if 'version' in local_dictionary:
                local_version = local_dictionary['version']
                if local_version['version'] != version['version']:
                    self.msg.append(u'Локальная версия справочника: {0}'.format(local_version))
                    self.msg.append(u'Актуальная версия справочника: {0}'.format(version))
                    self.msg.append(u'Версии не совпадают, обновляем diff')
                    data = self.client.getRefbookUpdate(code=dictionary['code'], user_version=local_version['version'])
                    return self.__add_data(dictionary['code'], data)
                else:
                    self.msg.append(u'Локальная версия справочника: {0}'.format(local_version))
                    self.msg.append(u'Актуальная версия справочника: {0}'.format(version))
                    self.msg.append(u'Версии совпадают, не обновляем справочник')
            else:
                self.msg.append(u'Локальная версия справочника не задана, импортируем данные')
                obj.update(_id=local_dictionary['_id'], data=dictionary)
                result = self.__add_parts_data(dictionary['code'], version['version'])
                if result:
                    self.msg.append(u'Справочник ({0}) обновлён'.format(dictionary['code']))
                    return True
        else:
            if overwrite:
                self.msg.append(u'Перезаписываем локальный справочник')
            else:
                self.msg.append(u'Локальный справочник не существует, импортируем данные')
            _id = obj.add(dictionary)
            result = self.__add_parts_data(dictionary['code'], version['version'])
            if result:
                self.msg.append(u'Справочник ({0}) обновлён'.format(dictionary['code']))
                return True
        return False

    def __get_latest_version(self, dictionary):
        nsi_dict_versions = self.__get_dictionary_versions(dictionary['code'])
        _versions = list()
        for version in nsi_dict_versions:
            _versions.append(self.__prepare_dictionary(version))
        try:
            latest_version = _versions[len(_versions) - 1]
        except IndexError, e:
            self.msg.append(e)
            latest_version = None
        else:
            try:
                latest_version['date'] = datetime.strptime(latest_version['date'], '%d.%m.%Y')
            except ValueError, e:
                self.msg.append(e)
                logger.error(u'Ошибка получения версии ({0}): {1}'.format(dictionary['code'], e),
                             extra=dict(tags=['nsi', 'import error']))
        return latest_version

    def __update_version(self, dictionary, version):
        obj = DictionaryNames()
        obj.update_by_code(dictionary['code'], dict(version=version))
        self.msg.append(u'Обновляем версию справочника ({0}): {1}'.format(dictionary['code'], version))

    def import_nsi_dictionaries(self, exclude=None, overwrite=False):
        nsi_dicts = self.__get_dictionaries()
        if nsi_dicts:
            for dict_data in nsi_dicts:
                nsi_dict = self.__prepare_dictionary(dict_data)
                if isinstance(exclude, list) and nsi_dict['code'] in exclude:
                    continue
                self.msg = list()
                latest_version = self.__get_latest_version(nsi_dict)
                result = self.__add_dict_data(nsi_dict, version=latest_version, overwrite=overwrite)
                if result:
                    self.__update_version(nsi_dict, latest_version)
                if DEBUG:
                    logger.debug(u'\n'.join(self.msg), extra=dict(tags=['nsi', 'import', nsi_dict['code']]))

    def create_indexes(self, collection_indexes):
        if not isinstance(collection_indexes, dict):
            return None
        for collection, indexes in collection_indexes.items():
            obj = Dictionary(collection)
            if not isinstance(indexes, list):
                indexes = [indexes]
            for index in indexes:
                for field, index_type in index.items():
                    obj.ensure_index(field, index_type)


def kladr_set_parents():
    dictionary = Dictionary('KLD172')
    limit = 1000
    for i in xrange(0, 300):
        print i
        documents = list(dictionary.get_list({'identparent': {'$ne': None}}, limit=limit, skip=i*limit))
        if not documents:
            break
        for document in documents:
            # print document['identcode']
            parent = dictionary.get_document({'identcode': document['identparent']})
            data = {'_id': document['_id']}
            if parent:
                data.update({'parent': parent['_id']})
            else:
                data.update({'parent': None})
            dictionary.add_document(data)