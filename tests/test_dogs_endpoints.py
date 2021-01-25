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


class TestDogsEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        """
        La base de datos debe estar vacia al comenzar el primer test
        """
        database.dogs.delete_many({})

    def tearDown(self) -> None:
        """
        Despues de cada test se debe limpiar la base de datos
        """
        database.dogs.delete_many({})

    def generate_document(self, name, is_adopted):
        response = requests.get('https://dog.ceo/api/breeds/image/random')

        document = {
            'name': name,
            'birth_date': datetime.now().isoformat(),
            'picture': response.json()['message'],
            'is_adopted': is_adopted,
            'id_user': ''
        }

        return document

    def register_document(self, name='Zeus', is_adopted=False):
        document = self.generate_document(name, is_adopted)
        result = database.dogs.insert_one(document)

        new_fields = {
            'ID': str(result.inserted_id),
            'created_date': str(result.inserted_id.generation_time.isoformat())
        }
        database.dogs.update_one({'_id': result.inserted_id},
                                 {'$set': new_fields})

        document = database.dogs.find_one({'_id': result.inserted_id})
        del document['_id']

        return document

    def read_document(self, ID):
        document = database.dogs.find_one({'_id': ID})
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
    def test_read_dogs_empty_database(self):
        response = client.get('/dogs')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    # @unittest.skip('Implementing test')
    def test_read_documents_one_element_database(self):
        document = self.register_document()

        # sin queries
        response = client.get('/dogs')
        received_document = response.json()[0]

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(received_document, document)

    # @unittest.skip('Implementing test')
    def test_read_documents_many_element_database(self):
        documents = []
        for i in range(10):
            adopted = bool(i % 2)
            document = self.register_document(is_adopted=adopted)
            documents.append(document)

        response = client.get('/dogs/?length=5&is_adopted=false')
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
        response = client.get('/dogs/?pastor_aleman=2')
        received_document = response.json()[0]

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(received_document, document)

    # @unittest.skip('Implementing test')
    def test_read_documents_queries_with_invalid_types(self):
        document = self.register_document()
        response = client.get('/dogs/?length=uno')
        self.assertEqual(response.status_code, 422)

    # @unittest.skip('Implementing test')
    def test_read_documents_queries_with_semantic_errors(self):
        document = self.register_document()

        # sin queries
        response = client.get('/dogs/?length=-1')
        self.assertEqual(response.status_code, 422)

    # @unittest.skip('Implementing test')
    def test_read_documents_queries_with_not_document_for_match(self):
        document = self.register_document()

        # sin queries
        response = client.get('/dogs/?id=no_existe')
        received_document = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(received_document, [])

    # @unittest.skip('Implementing test')
    def test_write_document(self):
        document = self.generate_document('Zeus', False)

        token = self.make_login()['access_token']

        response = client.post('/dogs/',
                               headers={
                                   'accept': 'application/json',
                                   'Authorization': 'Bearer %s' % token
                               },
                               json=document)
        self.assertEqual(response.status_code, 200)

        inserted_document = response.json()
        del inserted_document['ID']
        del inserted_document['created_date']

        # se debe buscar la forma de hacer la comparacion de las fechas
        del inserted_document['birth_date']
        del document['birth_date']

        self.assertDictEqual(inserted_document, document)

    # @unittest.skip('Implementing test')
    def test_write_document_not_logged(self):
        document = self.generate_document('Zeus', False)

        response = client.post('/dogs/',
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
        response = client.post('/dogs/',
                               headers={
                                   'accept': 'application/json',
                                   'Authorization': 'Bearer %s' % token
                               },
                               json={})

        self.assertEqual(response.status_code, 422)

    # @unittest.skip('Implementing test')
    def test_write_document_data_with_invalid_types(self):
        # en el nombre no importa el tipo que se ponga, siempre se hace un cast
        # implicito a str
        document = {
            'name': None,
            'birth_date': 'No es datetime',
            'picture': 'Hello World!!!',
            'is_adopted': 2.718281,
            'id_user': 235711
        }

        token = self.make_login()['access_token']

        response = client.post('/dogs/',
                               headers={
                                   'accept': 'application/json',
                                   'Authorization': 'Bearer %s' % token
                               },
                               json=document)
        self.assertEqual(response.status_code, 422)

    # @unittest.skip('Implementing test')
    def test_write_document_extra_data(self):
        document = self.generate_document('Zeus', False)
        correct_document = document.copy()

        # datos extra
        document['dato_extra_1'] = 'extra 1'
        document['dato_extra_2'] = 'extra 2'
        document['dato_extra_3'] = 'extra 3'

        token = self.make_login()['access_token']

        response = client.post('/dogs/',
                               headers={
                                   'accept': 'application/json',
                                   'Authorization': 'Bearer %s' % token
                               },
                               json=document)
        self.assertEqual(response.status_code, 200)

        inserted_document = response.json()
        del inserted_document['ID']
        del inserted_document['created_date']

        # se debe buscar la forma de hacer la comparacion de las fechas
        del inserted_document['birth_date']
        del correct_document['birth_date']

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
        response = client.delete('/dogs/?id=%s' % document['ID'])

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), document)

        # en realidad si fue borrado el documento
        self.assertIsNone(self.read_document(document['ID']))

    # @unittest.skip('Implementing test')
    def test_delete_nonexistent_document(self):
        response = client.delete('/dogs/?id=no_existe')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'], 'Item not found while deleting.')
