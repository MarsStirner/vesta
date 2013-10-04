# -*- coding: utf-8 -*-
from pymongo import MongoClient
from config import MONGODB_CONNECT_URI, MONGODB_DB, MONGODB_USER, MONGODB_PASSWORD


class MongoConnection:
    @classmethod
    def provider(cls, db_name, db_type='local'):
        connection, db = None, None
        if db_type == 'local':
            connection = MongoClient(MONGODB_CONNECT_URI)
            db = connection[db_name]
        if db and db_name != MONGODB_DB:
            db.authenticate(MONGODB_USER, MONGODB_PASSWORD)
        return connection, db