# -*- coding: utf-8 -*-
from datetime import datetime
import unittest
from app.app import app
from app.connectors import MongoConnection
from config import MONGODB_DB
from app.lib.data import Clients, DictionaryNames, Dictionary

TEST_DB = '{0}_test'.format(MONGODB_DB)
db_client, db = MongoConnection.provider(TEST_DB)


class DictionaryNamesTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['MONGODB_DB'] = TEST_DB
        self.app = app.test_client()
        self.obj = DictionaryNames()

    def tearDown(self):
        db.drop_collection(self.obj.code)

    def test_get_list(self):
        result = self.obj.get_list()
        self.assertEqual(result.count(), 0)
        self.assertEqual(list(result), list())

    def test_add(self):
        data = dict(code='test', name=u'Тестовый справочник')
        _id = self.obj.add(data)
        self.assertIsNotNone(_id)
        result = self.obj.get_by_id(_id)
        data.update(dict(_id=_id))
        self.assertDictEqual(data, result)

    def test_update(self):
        data = dict(code='test2', name=u'Тестовый справочник2')
        _id = self.obj.add(data)
        self.assertIsNotNone(_id)
        update_data = dict(code='test2', name=u'Тестовый справочник2 (updated)', updated=datetime.now())
        self.obj.update(_id, update_data)
        result = self.obj.get_by_id(_id)
        update_data.update(dict(_id=_id))
        result.pop('updated')
        update_data.pop('updated')
        self.assertDictEqual(result, update_data)

    def test_delete(self):
        code = 'test3'
        data = dict(code=code, name=u'Тестовый справочник3')
        _id = self.obj.add(data)
        self.assertIsNotNone(_id)
        self.obj.delete(code)
        result = self.obj.get_by_code(code)
        self.assertIsNone(result)

    def test_update_by_code(self):
        code = 'test4'
        data = dict(code=code, name=u'Тестовый справочник4')
        _id = self.obj.add(data)
        self.assertIsNotNone(_id)
        update_data = dict(code=code, name=u'Тестовый справочник4 (updated)', updated=datetime.now())
        self.obj.update_by_code(code, update_data)
        result = self.obj.get_by_code(code)
        update_data.update(dict(_id=_id))
        result.pop('updated')
        update_data.pop('updated')
        self.assertDictEqual(result, update_data)


class ClientsTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['MONGODB_DB'] = TEST_DB
        self.app = app.test_client()
        self.obj = Clients()

    def tearDown(self):
        db.drop_collection(self.obj.code)

    def test_get_list(self):
        result = self.obj.get_list()
        self.assertEqual(result.count(), 0)

    def test_add(self):
        data = dict(code='test', name=u'Тестовый клиент')
        _id = self.obj.add(data)
        self.assertIsNotNone(_id)
        result = self.obj.get_by_id(_id)
        data.update(dict(_id=_id))
        self.assertDictEqual(data, result)

    def test_update(self):
        data = dict(code='test2', name=u'Тестовый клиент2')
        _id = self.obj.add(data)
        self.assertIsNotNone(_id)
        update_data = dict(code='test2', name=u'Тестовый клиент2 (updated)', updated=datetime.now())
        self.obj.update(_id, update_data)
        result = self.obj.get_by_id(_id)
        update_data.update(dict(_id=_id))
        result.pop('updated')
        update_data.pop('updated')
        self.assertDictEqual(result, update_data)

    def test_delete(self):
        data = dict(code='test3', name=u'Тестовый клиент3')
        _id = self.obj.add(data)
        self.assertIsNotNone(_id)
        self.obj.delete(_id)
        result = self.obj.get_by_id(_id)
        self.assertIsNone(result)


class DictionaryTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['MONGODB_DB'] = TEST_DB
        self.app = app.test_client()
        self.collection = 'test_dictionary'
        self.obj = Dictionary(self.collection)

    def drop_collection(self):
        db.drop_collection(self.collection)

    def tearDown(self):
        db.drop_collection(self.collection)

    def test_get_list_empty(self):
        self.drop_collection()
        result = self.obj.get_list()
        self.assertRaises(ValueError)
        #self.assertEqual(result.count(), 0)

    def test_add_document(self):
        data = dict(code='test', name=u'Тестовый документ')
        _id = self.obj.add_document(data)
        self.assertIsNotNone(_id)
        result = self.obj.get_document(dict(_id=_id))
        data.update(dict(_id=_id))
        self.assertDictEqual(data, result)

    def test_add_documents(self):
        self.drop_collection()
        data = [dict(name=u'Документ1', code='document1'),
                dict(name=u'Документ2'),
                dict(name=u'Документ3', alias='document2'),
                dict(name=u'Документ4', code='document4', created=datetime.now())]
        _ids = self.obj.add_documents(data)
        self.assertIsNotNone(_ids)
        self.assertIsInstance(_ids, list)
        result = list(self.obj.get_list())
        self.assertEqual(len(result), len(data))
        self.assertEqual(result[0]['code'], data[0]['code'])
        data_2 = data[2]
        data_2.update(dict(_id=_ids[2]))
        self.assertEqual(result[2], data_2)

    def test_get_document(self):
        data = dict(code='test5', name=u'Тестовый документ5')
        _id = self.obj.add_document(data)
        self.assertIsNotNone(_id)
        result = self.obj.get_document(dict(_id=_id))
        data.update(dict(_id=_id))
        self.assertDictEqual(data, result)

    def test_count_documents(self):
        self.drop_collection()
        data = [dict(name=u'Документ1', code='document1'),
                dict(name=u'Документ2'),
                dict(name=u'Документ3', alias='document2'),
                dict(name=u'Документ4', code='document4', created=datetime.now())]
        _ids = self.obj.add_documents(data)
        self.assertIsNotNone(_ids)
        self.assertIsInstance(_ids, list)
        result = self.obj.count()
        self.assertEqual(result, len(data))
        result = self.obj.count(dict(_id=_ids[0]))
        self.assertEqual(result, 1)
        result = self.obj.count(dict(_id='not_exists_id'))
        self.assertEqual(result, 0)

    def test_delete(self):
        data = dict(code='test_delete', name=u'Тестовый документ')
        _id = self.obj.add_document(data)
        self.assertIsNotNone(_id)
        self.obj.delete(_id)
        result = self.obj.get_document(dict(_id=_id))
        self.assertIsNone(result)

    def test_exists(self):
        self.drop_collection()
        data = [dict(name=u'Документ1', code='document1'),
                dict(name=u'Документ2'),
                dict(name=u'Документ3', alias='document2'),
                dict(name=u'Документ4', code='document4', created=datetime.now())]
        _ids = self.obj.add_documents(data)
        self.assertIsNotNone(_ids)
        self.assertIsInstance(_ids, list)
        result = self.obj.exists()
        self.assertTrue(result)
        result = self.obj.count(dict(_id=_ids[0]))
        self.assertTrue(result)
        result = self.obj.count(dict(_id='not_exists_id'))
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
