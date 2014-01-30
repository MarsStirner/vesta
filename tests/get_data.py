# -*- coding: utf-8 -*-
from datetime import datetime
import unittest
from app.app import app
from app.connectors import MongoConnection
from config import MONGODB_DB, SERVER_HOST, SERVER_PORT
from app.lib.utils.tools import json


class GetDataTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.api_url = 'http://{host}:{port}/api/'.format(host=SERVER_HOST, port=SERVER_PORT)
        self.collection_code = 'NK0469'

    def test_post_doc(self):
        data = dict(code=u'01')
        response = self.app.post(self.api_url + self.collection_code + '/', data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.get_data())
        #response.pop('_id')
        self.assertEqual(self.collection_code, response['code'])


if __name__ == '__main__':
    unittest.main()
