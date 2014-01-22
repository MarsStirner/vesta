# -*- coding: utf-8 -*-
from exceptions import Exception, ValueError


class RefbookTooLargeError(Exception):
    code = '03x0003'
    message = u'Ошибка справочника: Справочник слишком велик'