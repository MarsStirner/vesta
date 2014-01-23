#-*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .config import DB_CONNECT_STRING

engine = create_engine(DB_CONNECT_STRING, convert_unicode=True, pool_recycle=600)
connection = engine.connect()


def db_disconnect():
    connection.close()
