from pymongo import MongoClient

from ..logger import logger
from ..logs.database_messages import *

import os

from .celery import app


@app.task
def add_document_to_database(collection, document):
    # cuando se esta en desarrollo la variable de entorno debe tomar el valor de
    # 'localhost', cuando se piense correr en un docker, deberia ser mongo
    MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
    logger.info('Mongo host set to: %s' % MONGO_HOST)

    logger.info(CONNECTING_TO_DB)
    # por defecto mongo inicia su servicio en el puerto 27017, si se quiere cambiar
    # este numero se debe forzar a lanzar el servicio por otro puerto
    client = MongoClient(host=MONGO_HOST, port=27017)
    database = client.guane_inter_fast_api

    result = database[collection].insert_one(document)

    new_fields = {'ID': str(result.inserted_id)}
    if collection == 'dogs':
        new_fields['created_date'] = result.inserted_id.generation_time
    database[collection].update_one({'_id': result.inserted_id},
                                    {'$set': new_fields})

    document = database[collection].find_one({'_id': result.inserted_id})
    del document['_id']

    return document
