import unittest

import logging
# se desabilita el sistema de logs del API
logging.disable(logging.CRITICAL)

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


root_response = '''<html>
    <head>
        <title>Guane Inter FastAPI</title>
    </head>
    <body>
        <h1>Hello World!!!</h1>
    </body>
</html>'''


class TestMainEndpoints(unittest.TestCase):
    def test_root_endpoint(self):
        response = client.get('/')

        text = response.text

        self.assertEqual(root_response, text)

    def make_login(self, username, password):
        response = client.post('/token',
                               headers={'accept': 'application/json',
                                        'Content-Type': 'application/x-www-form-urlencoded'},
                               data={'username': username,
                                     'password': password})

        return response.json()

    def test_perfect_login(self):
        token_data = self.make_login('Luispapiernik', 'Luispapiernik')

        keys = token_data.keys()
        self.assertIn('access_token', keys)
        self.assertIn('token_type', keys)

        self.assertIsInstance(token_data['access_token'], str)
        self.assertEqual(token_data['token_type'], 'bearer')

    def test_login_invalid_credentials(self):
        error_data = self.make_login('invalid_user', 'incorrect_password')

        keys = error_data.keys()
        self.assertIn('detail', keys)
        self.assertEqual(error_data['detail'], 'Incorrect username or password')
