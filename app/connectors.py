# -*- coding: utf-8 -*-
from pymongo import MongoClient
from config import MONGODB_CONNECT_URI, MONGODB_DB

db_local_client = MongoClient(MONGODB_CONNECT_URI)