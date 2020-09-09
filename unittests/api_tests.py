import unittest

from app.api import create_app

class ApiTest(unittest.TestCase):

    def setUp(self):
        self._client = create_app().test_client()

    # Testamos se a resposta e 200 ("ok")
    def test_01(self):
        response = self._client.get('/')
        self.assertEqual(200, response.status_code)
