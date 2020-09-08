import unittest

from app.api import create_app

class ApiTest(unittest.TestCase):

    '''
      Como todos os 3 casos de teste fazem um get na home "/"
      da nossa aplicacao, definimos a funcao setUp. Ela e executada
      automaticamente sempre que o Pytest instancia a classe TestHomeView.
      A funcao setUp e semelhante a um metodo construtor.
    '''

    def setUp(self):
        app = create_app().test_client()
        self.response = app.get('/')

    # Testamos se a resposta e 200 ("ok")
    def test_get(self):
        self.assertEqual(200, self.response.status_code)

    # # Testamos se a nossa home retorna a string "ok"
    # def test_html_string_response(self):
    #     self.assertEqual("ok", self.response.data.decode('utf-8'))

    # # Testamos se o content_type da resposta da home esta correto
    # def test_content_type(self):
    #     self.assertIn('text/html', self.response.content_type)