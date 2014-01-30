# -*- coding: utf-8 -*-
from pymongo import MongoClient
from config import MONGODB_CONNECT_URI, MONGODB_DB, MONGODB_USER, MONGODB_PASSWORD, MONGODB_HOST


class MongoConnection:
    @classmethod
    def provider(cls, db_name=None, db_type='local'):
        connection, db = None, None
        if db_type == 'local':
            connection = MongoClient(MONGODB_HOST, tz_aware=True)
            if db_name is None:
                db_name = MONGODB_DB
            if MONGODB_USER and MONGODB_PASSWORD:
                connection[db_name].authenticate(MONGODB_USER, MONGODB_PASSWORD, source=db_name)
            db = connection[db_name]
        return connection, db