# -*- coding: utf-8 -*-
DEBUG = False

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
SYSTEM_USER = 'vesta'

MODULE_NAME = 'vesta'

WTF_CSRF_ENABLED = True
SECRET_KEY = ''

MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_USER = 'vesta_user'
MONGODB_PASSWORD = 'vesta_pwd'
MONGODB_DB = 'vesta'

SIMPLELOGS_URL = 'http://127.0.0.1:8080'
NSI_SOAP = 'http://nsi.rosminzdrav.ru/wsdl/service.v2.wsdl'
NSI_TOKEN = ''

try:
    from config_local import *
except ImportError:
    # no local config found
    pass

MONGODB_CONNECT_URI = 'mongodb://{user}:{password}@{host}/{database}'.format(user=MONGODB_USER,
                                                                             password=MONGODB_PASSWORD,
                                                                             host=MONGODB_HOST,
                                                                             port=MONGODB_PORT,
                                                                             database=MONGODB_DB)