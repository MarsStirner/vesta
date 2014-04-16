#-*- coding: utf-8 -*-
from sqlalchemy import create_engine, MetaData

from .config import DB_CONNECT_STRING

engine = create_engine(DB_CONNECT_STRING, convert_unicode=True, pool_recycle=600)
meta = MetaData(engine)
meta.reflect(bind=engine, views=True, only=lambda name, obj: name.startswith(u'rb') and not name.startswith(u'rb_'))
connection = engine.connect()


def db_disconnect():
    connection.close()
