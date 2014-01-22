# -*- coding: utf-8 -*-
from config import NSI_SOAP, NSI_TOKEN
from client import NSI_Client
from ..data import *


class NSI_Data:

    def __init__(self):
        self.msg = list()
        self.client = NSI_Client(url=NSI_SOAP, user_key=NSI_TOKEN)

    def __get_dictionaries(self):
        result = self.client.getRefbookList()
        return result

    def __get_dictionary(self, code, version):
        result = self.client.getRefbook(code, version)
        return result

    def __get_local_dictionary(self, code):
        obj = DictionaryNames()
        return obj.get_by_code(code)

    def __get_dictionary_versions(self, code):
        result = self.client.getVersionList(code)
        return result

    def __get_data(self, dictionary):
        obj = DictionaryNames()
        data = dict()
        local_dictionary = self.__get_local_dictionary(dictionary['code'])
        self.msg.append(u'Импорт {0} ({1})'.format(dictionary['name'], dictionary['code']))
        if local_dictionary:
            if 'version' in local_dictionary:
                local_version = local_dictionary['version']
                if local_version != dictionary['version']:
                    self.msg.append(u'Локальная версия справочника: {0}'.format(local_version))
                    self.msg.append(u'Актуальная версия справочника: {0}'.format(dictionary['version']))
                    self.msg.append(u'Версии не совпадают, обновляем diff')
                    data = self.client.getRefbookUpdate(code=dictionary['code'], user_version=local_version)
            else:
                version = dictionary.pop('version')
                self.msg.append(u'Локальная версия справочника не задана, импортируем данные')
                obj.update(_id=local_dictionary['_id'], data=dictionary)
                data = self.client.getRefbook(dictionary['code'], version)
        else:
            version = dictionary.pop('version')
            self.msg.append(u'Локальный справочник не существует, импортируем данные')
            obj.update(_id=local_dictionary['_id'], data=dictionary)
            _id = obj.add(dictionary)
            data = self.client.getRefbook(dictionary['code'], version)
        return data

    def __add_data(self, code, data):
        obj = Dictionary(code)
        for document in data:
            exists_document = obj.get_document(dict(code=document['code']))
            if exists_document:
                document.update(dict(_id=exists_document['_id']))
            self.msg.append(u'Добавляем документ {0}'.format(document))
            try:
                result = obj.add_document(document)
            except AttributeError, e:
                self.msg.append(e)
                return False
            else:
                self.msg.append(u'{0}'.format(result))
        return True

    def __update_version(self, dictionary):
        obj = DictionaryNames()
        obj.update_by_code(dictionary['code'], dict(version=dictionary['version']))
        self.msg.append(u'Обновляем версию справочника ({0}): {1}'.format(dictionary['code'], dictionary['version']))

    def import_nsi_dictionaries(self):
        # TODO: add logging
        nsi_dicts = self.__get_dictionaries()
        if nsi_dicts:
            for nsi_dict in nsi_dicts:
                self.msg = list()
                data = self.__get_data(nsi_dict)
                if data:
                    result = self.__add_data(nsi_dict['code'], data)
                    if result:
                        self.__update_version(nsi_dict)
                logger.debug(self.msg, extra=dict(tags=['nsi', 'import', nsi_dict['code']]))