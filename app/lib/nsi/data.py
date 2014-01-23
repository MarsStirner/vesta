# -*- coding: utf-8 -*-
from datetime import datetime
from config import NSI_SOAP, NSI_TOKEN
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

    def __get_data(self, dictionary, version):
        obj = DictionaryNames()
        data = dict()
        local_dictionary = self.__get_local_dictionary(dictionary['code'])
        self.msg.append(u'Импорт {0} ({1})'.format(dictionary['name'], dictionary['code']))
        if local_dictionary:
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
            self.msg.append(u'Локальный справочник не существует, импортируем данные')
            _id = obj.add(dictionary)
            data = self.__get_dictionary(dictionary['code'], version['version'])
        return data

    def __doc_info(self, document):
        return u', '.join([u'{0}: {1}'.format(key, value) for key, value in document.iteritems()])

    def __add_data(self, code, data):
        obj = Dictionary(code)
        for document_data in data:
            existdocument = None
            document = self.__prepare_dictionary(document_data)
            if not document:
                continue
            if 'code' in document:
                existdocument = obj.get_document(dict(code=document['code']))
            elif 'id' in document:
                existdocument = obj.get_document(dict(id=document['id']))
            if existdocument:
                document.update(dict(_id=existdocument['_id']))
            # self.msg.append(u'Обновляем документ ({0})'.format(self.__doc_info(document)))
            try:
                result = obj.add_document(document)
            except AttributeError, e:
                logger.error(
                    self.msg.append(u'Ошибка импорта документа ({0}): {1}'.format(self.__doc_info(document), e)),
                    extra=dict(tags=['nsi', 'import error']))
                return False
            # else:
            #     self.msg.append(u'{0}'.format(result))
        return True

    def __get_latest_version(self, dictionary):
        nsi_dict_versions = self.__get_dictionary_versions(dictionary['code'])
        _versions = list()
        for version in nsi_dict_versions:
            _versions.append(self.__prepare_dictionary(version))
        try:
            latest_version = _versions[0]
        except IndexError, e:
            self.msg.append(e)
            latest_version = None
        else:
            try:
                latest_version['date'] = datetime.strptime(latest_version['date'], '%d.%m.%Y')
            except ValueError, e:
                self.msg.append(e)
        return latest_version

    def __update_version(self, dictionary, version):
        obj = DictionaryNames()
        obj.update_by_code(dictionary['code'], dict(version=version))
        self.msg.append(u'Обновляем версию справочника ({0}): {1}'.format(dictionary['code'], version))

    def import_nsi_dictionaries(self, exclude=None):
        nsi_dicts = self.__get_dictionaries()
        if nsi_dicts:
            for dict_data in nsi_dicts:
                nsi_dict = self.__prepare_dictionary(dict_data)
                if isinstance(exclude, list) and nsi_dict['code'] in exclude:
                    continue
                self.msg = list()
                latest_version = self.__get_latest_version(nsi_dict)
                data = self.__get_data(nsi_dict, version=latest_version)
                if data:
                    result = self.__add_data(nsi_dict['code'], data)
                    if result:
                        self.__update_version(nsi_dict, latest_version)
                logger.debug(u'\n'.join(self.msg), extra=dict(tags=['nsi', 'import', nsi_dict['code']]))