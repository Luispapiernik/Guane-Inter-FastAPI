import unittest

import logging
# se desabilita el sistema de logs del API
logging.disable(logging.CRITICAL)

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestDogsEndpoints(unittest.TestCase):
    def test_get_dogs(self):
        response = client.get('/dogs/')
