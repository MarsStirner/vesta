# -*- coding: utf-8 -*-
from config import NSI_SOAP, NSI_TOKEN, DEBUG
from suds.client import Client
from suds import WebFault
from app.lib.utils.tools import logger


class NSI_Client:
    """Класс SOAP-клиента для взаимодействия со сервисом НСИ"""
    def __init__(self):
        self.user_key = NSI_TOKEN
        if DEBUG:
            self.client = Client(NSI_SOAP, cache=None)
        else:
            self.client = Client(NSI_SOAP)

    def getRefbook(self, code, version):
        try:
            result = self.client.service.getRefbook(userKey=self.user_key, refbookCode=code, version=version)
        except WebFault, e:
            print e
            logger.error(e, extra=dict(tags=['getRefbook', 'nsi']))
        else:
            return result
        return None

    def getRefbookList(self):
        try:
            result = self.client.service.getRefbookList(userKey=self.user_key)
        except WebFault, e:
            print e
            logger.error(e, extra=dict(tags=['getRefbookList', 'nsi']))
        else:
            return result
        return None

    def getRefbookPartial(self, code, version, part_number):
        try:
            result = self.client.service.getRefbookPartial(userKey=self.user_key,
                                                           refbookCode=code,
                                                           version=version,
                                                           partNumber=part_number)
        except WebFault, e:
            print e
            logger.error(e, extra=dict(tags=['getRefbookPartial', 'nsi']))
        else:
            return result
        return None

    def getRefbookParts(self, code, version):
        try:
            result = self.client.service.getRefbookParts(userKey=self.user_key, refbookCode=code, version=version)
        except WebFault, e:
            print e
            logger.error(e, extra=dict(tags=['getRefbookParts', 'nsi']))
        else:
            return result
        return None

    def getRefbookUpdate(self, code, user_version=None, new_version=None):
        try:
            parameters = dict(userKey=self.user_key, refbookCode=code)
            if user_version is not None:
                parameters['userVersion'] = user_version
            if new_version is not None:
                parameters['newVersion'] = new_version
            result = self.client.service.getRefbookUpdate(**parameters)
        except WebFault, e:
            print e
            logger.error(e, extra=dict(tags=['getRefbookUpdate', 'nsi']))
        else:
            return result
        return None

    def getServerTime(self):
        try:
            result = self.client.service.getServerTime()
        except WebFault, e:
            print e
            logger.error(e, extra=dict(tags=['getServerTime', 'nsi']))
        else:
            return result
        return None

    def getVersionList(self, code):
        try:
            result = self.client.service.getVersionList(userKey=self.user_key, refbookCode=code)
        except WebFault, e:
            print e
            logger.error(e, extra=dict(tags=['getVersionList', 'nsi']))
        else:
            return result
        return None