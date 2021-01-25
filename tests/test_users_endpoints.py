import unittest
import logging
import os

# se desabilita el sistema de logs del API
logging.disable(logging.CRITICAL)

from fastapi.testclient import TestClient
from app.main import app

from datetime import datetime
from pymongo import MongoClient
import requests

# cuando se esta en desarrollo la variable de entorno debe tomar el valor de
# 'localhost', cuando se piense correr en un docker, deberia ser mongo
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')

# por defecto mongo inicia su servicio en el puerto 27017, si se quiere cambiar
# este numero se debe forzar a lanzar el servicio por otro puerto
mongo_client = MongoClient(host=MONGO_HOST, port=27017)
database = mongo_client.guane_inter_fast_api

client = TestClient(app)


class TestUsersEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        """
        La base de datos debe estar vacia al comenzar el primer test
        """
        database.users.delete_many({})

    def tearDown(self) -> None:
        """
        Despues de cada test se debe limpiar la base de datos
        """
        database.users.delete_many({})

    def generate_document(self, name, last_name, email):
        document = {
            'name': name,
            'last_name': last_name,
            'email': email
        }

        return document

    def register_document(self, name='Luis', last_name='Papiernik', email=None):
        document = self.generate_document(name, last_name, email)
        result = database.users.insert_one(document)

        new_fields = {
            'ID': str(result.inserted_id)
        }
        database.users.update_one({'_id': result.inserted_id},
                                 {'$set': new_fields})

        document = database.users.find_one({'_id': result.inserted_id})
        del document['_id']

        return document

    def read_document(self, ID):
        document = database.users.find_one({'_id': ID})
        try:
            del document['_id']
        except TypeError:
            # se llega aqui si el documento no existe
            pass

        return document

    def make_login(self):
        response = client.post('/token',
                               headers={'accept': 'application/json',
                                        'Content-Type': 'application/x-www-form-urlencoded'},
                               data={'username': 'Luispapiernik',
                                     'password': 'Luispapiernik'})

        return response.json()

    # @unittest.skip('Implementing test')
    def test_read_users_empty_database(self):
        response = client.get('/users')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    # @unittest.skip('Implementing test')
    def test_read_documents_one_element_database(self):
        document = self.register_document()

        # sin queries
        response = client.get('/users')
        received_document = response.json()[0]

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(received_document, document)

    # @unittest.skip('Implementing test')
    def test_read_documents_many_element_database(self):
        documents = []
        for i in range(10):
            document = self.register_document(['Luis', 'Santiago'][i % 2])
            documents.append(document)

        response = client.get('/users/?length=5&name=Luis')
        received_documents = response.json()

        self.assertEqual(len(received_documents), 5)
        for received_document in received_documents:
            for document in documents:
                if received_document['ID'] == document['ID']:
                    self.assertDictEqual(received_document, document)

    # @unittest.skip('Implementing test')
    def test_read_document_nonexistent_queries(self):
        document = self.register_document()

        # se ignoran los queries no esperados
        response = client.get('/users/?dogs=2')
        received_document = response.json()[0]

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(received_document, document)

    # @unittest.skip('Implementing test')
    def test_read_documents_queries_with_invalid_types(self):
        document = self.register_document()
        response = client.get('/users/?length=uno')
        self.assertEqual(response.status_code, 422)

    # @unittest.skip('Implementing test')
    def test_read_documents_queries_with_semantic_errors(self):
        document = self.register_document()

        # sin queries
        response = client.get('/users/?length=-1')
        self.assertEqual(response.status_code, 422)

    # @unittest.skip('Implementing test')
    def test_read_documents_queries_with_not_document_for_match(self):
        document = self.register_document()

        # sin queries
        response = client.get('/users/?id=no_existe')
        received_document = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_document, [])

    # @unittest.skip('Implementing test')
    def test_write_document(self):
        document = self.generate_document('Luis', 'Papiernik', None)

        token = self.make_login()['access_token']

        response = client.post('/users/',
                               headers={
                                   'accept': 'application/json',
                                   'Authorization': 'Bearer %s' % token
                               },
                               json=document)
        self.assertEqual(response.status_code, 200)

        inserted_document = response.json()
        del inserted_document['ID']

        self.assertDictEqual(inserted_document, document)

    # @unittest.skip('Implementing test')
    def test_write_document_not_logged(self):
        document = self.generate_document('Luis', 'Papiernik', None)

        response = client.post('/users/',
                               headers={
                                   'accept': 'application/json'
                               },
                               json=document)

        error_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(error_data.get('detail', None), 'Not authenticated')

    # @unittest.skip('Implementing test')
    def test_write_document_without_data(self):
        token = self.make_login()['access_token']
        response = client.post('/users/',
                               headers={
                                   'accept': 'application/json',
                                   'Authorization': 'Bearer %s' % token
                               },
                               json={})

        self.assertEqual(response.status_code, 422)

    # @unittest.skip('Implementing test')
    def test_write_document_data_with_invalid_types(self):
        # en el nombre no importa el tipo que se ponga, siempre se hace un cast
        # implicito a str, similar last_name
        document = {
            'name': None,
            'last_name': None,
            'email': 3.141592
        }

        token = self.make_login()['access_token']

        response = client.post('/users/',
                               headers={
                                   'accept': 'application/json',
                                   'Authorization': 'Bearer %s' % token
                               },
                               json=document)

        self.assertEqual(response.status_code, 422)

    # @unittest.skip('Implementing test')
    def test_write_document_extra_data(self):
        document = self.generate_document('Luis', 'Papiernik', None)
        correct_document = document.copy()

        # datos extra
        document['dato_extra_1'] = 'extra 1'
        document['dato_extra_2'] = 'extra 2'
        document['dato_extra_3'] = 'extra 3'

        token = self.make_login()['access_token']

        response = client.post('/users/',
                               headers={
                                   'accept': 'application/json',
                                   'Authorization': 'Bearer %s' % token
                               },
                               json=document)
        self.assertEqual(response.status_code, 200)

        inserted_document = response.json()
        del inserted_document['ID']

        self.assertDictEqual(inserted_document, correct_document)

    @unittest.skip('Implementing test')
    def test_update_document(self):
        pass

    @unittest.skip('Implementing test')
    def test_update_document_not_logged(self):
        pass

    @unittest.skip('Implementing test')
    def test_update_nonexistent_document(self):
        pass

    @unittest.skip('Implementing test')
    def test_update_document_without_passing_data(self):
        pass

    @unittest.skip('Implementing test')
    def test_update_document_data_with_invalid_types(self):
        pass

    @unittest.skip('Implementing test')
    def test_update_document_data_another_model(self):
        pass

    @unittest.skip('Implementing test')
    def test_update_document_extra_data(self):
        pass

    # @unittest.skip('Implementing test')
    def test_delete_document(self):
        document = self.register_document()

        # sin queries
        response = client.delete('/users/?id=%s' % document['ID'])

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), document)

        # en realidad si fue borrado el documento
        self.assertIsNone(self.read_document(document['ID']))

    # @unittest.skip('Implementing test')
    def test_delete_nonexistent_document(self):
        response = client.delete('/users/?id=no_existe')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'], 'Item not found while deleting.')
