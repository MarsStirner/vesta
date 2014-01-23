# -*- coding: utf-8 -*-
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'q1w2e3r4t5'
DB_NAME = 'ntk_reference_162'

DB_CONNECT_STRING = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

refbooks = ['rbAcheResult',
            'rbDocumentType',
            'rbFinance',
            'rbOKVED',
            'rbPost',
            'rbResult',
            'rbSocStatusClassTypeAssoc',
            'rbSocStatusType',
            'rbSpeciality',
            'rbTraumaType']