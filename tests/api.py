# -*- coding: utf-8 -*-
from datetime import datetime
import unittest
from app.app import app
from app.connectors import MongoConnection
from config import MONGODB_DB, SERVER_HOST, SERVER_PORT
from app.lib.utils.tools import json


TEST_DB = '{0}_test'.format(MONGODB_DB)
db_client, db = MongoConnection.provider(TEST_DB)


class DictionaryNamesAPITestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['MONGODB_DB'] = TEST_DB
        self.app = app.test_client()
        self.collection = 'dict_names'
        self.api_url = 'http://{host}:{port}/dictionaries/'.format(host=SERVER_HOST, port=SERVER_PORT)

    def tearDown(self):
        db.drop_collection(self.collection)

    def test_get_dictionaries(self):
        response = self.app.get(self.api_url)
        self.assertEqual(response.status_code, 200)

    def get_by_code(self, code=None):
        response = None
        if code is not None:
            response = self.app.get(self.api_url + code + '/')
        return response

    def test_add_dictionary(self):
        code = 'test'
        data = dict(code=code, name=u'Тестовый справочник')
        response = self.app.post(self.api_url, data=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        response = self.get_by_code(code)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_data())
        self.assertDictContainsSubset(data, response_data)

    def test_put_dictionary(self):
        code = 'test2'
        data = dict(code=code, name=u'Тестовый справочник2')
        response = self.app.post(self.api_url, data=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        data_update = dict(name=u'Тестовый справочник2 (обновлён)')
        response = self.app.put(self.api_url + code + '/', data=json.dumps(data_update))
        self.assertEqual(response.status_code, 200)
        response = self.get_by_code(code)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_data())
        self.assertEqual(data_update['name'], response_data['name'])

    def test_delete_dictionary(self):
        code = 'test3'
        data = dict(code=code, name=u'Тестовый справочник3')
        response = self.app.post(self.api_url, data=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        response = self.app.delete(self.api_url + code + '/')
        self.assertEqual(response.status_code, 204)
        response = self.get_by_code(code)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_data())
        self.assertIsNone(response_data.get('result'))


class ClientsAPITestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['MONGODB_DB'] = TEST_DB
        self.app = app.test_client()
        self.collection = 'clients'
        self.api_url = 'http://{host}:{port}/clients/'.format(host=SERVER_HOST, port=SERVER_PORT)

    def tearDown(self):
        db.drop_collection(self.collection)

    def test_get_dictionaries(self):
        response = self.app.get(self.api_url)
        self.assertEqual(response.status_code, 200)

    def get_by_code(self, code=None):
        response = None
        if code is not None:
            response = self.app.get(self.api_url + code + '/')
        return response

    def test_add_dictionary(self):
        code = 'test'
        data = dict(code=code, name=u'Тестовый клиент')
        response = self.app.post(self.api_url, content_type='application/json', data=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        response = self.get_by_code(code)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.get_data())
        result.pop('_id')
        self.assertDictEqual(data, result)

    def test_put_dictionary(self):
        code = 'test2'
        data = dict(code=code, name=u'Тестовый клиент2')
        response = self.app.post(self.api_url, content_type='application/json', data=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        data_update = dict(name=u'Тестовый клиент2 (обновлён)')
        response = self.app.put(self.api_url + code + '/', data=json.dumps(data_update))
        self.assertEqual(response.status_code, 200)
        response = self.get_by_code(code)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_data())
        self.assertDictContainsSubset(data_update, response_data)

    def test_delete_dictionary(self):
        code = 'test3'
        data = dict(code=code, name=u'Тестовый клиент3')
        response = self.app.post(self.api_url, data=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        response = self.app.delete(self.api_url + code + '/')
        self.assertEqual(response.status_code, 204)
        response = self.get_by_code(code)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_data())
        self.assertIsNone(response_data.get('result'))


class DictionaryAPITestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['MONGODB_DB'] = TEST_DB
        self.app = app.test_client()
        self.collection_code = 'test_dict'
        self.api_url = 'http://{host}:{port}/dictionary/'.format(host=SERVER_HOST, port=SERVER_PORT)

    def tearDown(self):
        db.drop_collection(self.collection_code)

    def get_documents(self, code):
        response = self.app.get(self.api_url + code + '/')
        return response

    def get_document(self, code, _id):
        response = self.app.get(self.api_url + '/'.join((code, _id, '')))
        return response

    def test_get_documents404(self):
        response = self.get_documents(self.collection_code)
        self.assertEqual(response.status_code, 404)

    def test_get_document404(self):
        response = self.get_document(self.collection_code, '123')
        self.assertEqual(response.status_code, 404)

    def test_post_list(self):
        data = [dict(name=u'Документ1', code='document1'),
                dict(name=u'Документ2'),
                dict(name=u'Документ3', alias='document2'),
                dict(name=u'Документ4', code='document4', created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))]
        response = self.app.post(self.api_url + self.collection_code + '/', data=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.get_data())
        post_result = json.loads(response.get_data())
        post_result = post_result.get('_id')
        self.assertIsInstance(post_result, list)
        document_id = post_result[0]
        response = self.get_document(self.collection_code, document_id)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.get_data())
        self.assertDictContainsSubset(data[0], response)

    def test_post_doc(self):
        data = dict(name=u'Документ5', code='document5', created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        response = self.app.post(self.api_url + self.collection_code + '/', data=json.dumps(data))
        post_result = json.loads(response.get_data())
        self.assertEqual(response.status_code, 201)
        document_id = post_result.get('_id')
        self.assertIsNotNone(document_id)
        self.assertIsInstance(document_id, basestring)
        response = self.get_document(self.collection_code, document_id)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.get_data())
        #response.pop('_id')
        self.assertDictContainsSubset(data, response)

    def test_put_doc(self):
        data = dict(name=u'Документ6', code='document6', created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        response = self.app.post(self.api_url + self.collection_code + '/', data=json.dumps(data))
        post_result = json.loads(response.get_data())
        document_id = post_result.get('_id')
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(document_id)
        self.assertIsInstance(document_id, basestring)
        update_data = dict(name=u'Документ6 (updated)', updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        response = self.app.put(self.api_url + '/'.join((self.collection_code, document_id, '')),
                                data=json.dumps(update_data))
        self.assertEqual(response.status_code, 200)
        response = self.get_document(self.collection_code, document_id)
        modified_data = data
        modified_data.pop('name')
        modified_data.update(update_data)
        modified_data.update(dict(_id=document_id))
        response = json.loads(response.get_data())
        self.assertDictContainsSubset(modified_data, response)

    def test_del_doc(self):
        data = dict(name=u'Документ7', code='document7', created=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        response = self.app.post(self.api_url + self.collection_code + '/', data=json.dumps(data))
        post_result = json.loads(response.get_data())
        document_id = post_result.get('_id')
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(document_id)
        response = self.app.delete(self.api_url + '/'.join((self.collection_code, document_id, '')))
        self.assertEqual(response.status_code, 204)
        response = self.get_document(self.collection_code, document_id)
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
