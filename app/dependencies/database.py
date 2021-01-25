from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Union
from pydantic import BaseModel
from fastapi import Query, Depends, HTTPException

from ..logger import logger
from ..logs.database_messages import *

from ..models.dog import DogIn
from ..models.user import UserIn

from ..worker.tasks import add_document_to_database

import os

# cuando se esta en desarrollo la variable de entorno debe tomar el valor de
# 'localhost', cuando se piense correr en un docker, deberia ser mongo
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
logger.info('Mongo host set to: %s' % MONGO_HOST)

logger.info(CONNECTING_TO_DB)
# por defecto mongo inicia su servicio en el puerto 27017, si se quiere cambiar
# este numero se debe forzar a lanzar el servicio por otro puerto
client = AsyncIOMotorClient(host=MONGO_HOST, port=27017)
database = client.guane_inter_fast_api


class QueryFields(BaseModel):
    """
    Representación de los queries hechos por el usuario como variables de una
    clase.
    """
    length: Optional[int] = Query(1, gt=0)
    ID: Optional[str] = Query(None, alias='id')
    name: Optional[str] = Query(None)
    last_name: Optional[str] = Query(None)
    is_adopted: Optional[bool] = Query(None)
    id_user: Optional[str] = Query(None)


class DatabaseManager:
    """
    Clase que se encarga de hacer la operación requerida (consulta, escritura
    actualización o borrado), según la colección (dogs o users) que se este
    usando.
    """
    def __init__(self, collection):
        self.collection = collection

    def get_query_dict(self, query_fields: QueryFields):
        """
        De una instancia de la clase QueryFields se eliminan los parametros
        que no sean validos para la colección actual.

        Parameters
        ----------
        query_fields : QueryFields
            Clase cuyos atributos son los queries hechos por el usuario.

        Returns
        -------
        out : dict
            Diccionario con los queries validos para la colección usada.
        """
        # se obtienen los queries y sus valores como un diccionario
        params = query_fields.dict()

        # en base de datos a los documentos no se les esta guardando un atributo
        # length
        del params['length']
        if self.collection == 'dogs':
            # los dogs no tienen el atributo last_name
            del params['last_name']
        if self.collection == 'users':
            # los users no tienen los atributos is_adopted ni id_user
            del params['is_adopted']
            del params['id_user']

        # si el campo es nulo, no aporta información para la búsqueda
        params = {key: value for (key, value) in params.items()
                  if value is not None}

        return params

    async def get_documents_from_db(self, query_fields: QueryFields = Depends()):
        """
        Se consultan documentos de la base de datos de acuerdo a parámetros de
        búsqueda.

        Parameters
        ----------
        query_fields : QueryFields
            Clase cuyos atributos son los parámetros de búsqueda especificados
            por el usuario.

        Returns
        -------
        out : List[Union[DogOut, UserOut].dict()]
            Lista con la información de los documentos.
        """
        logger.info(GET_DOCUMENT)
        params = self.get_query_dict(query_fields)
        cursor = database[self.collection].find(params)

        # no se puede retornar una coroutine porque FastApi aplica una conversion
        # sobre los resultados que retornan las dependencias para pasarlos a
        # las path functions
        documents = await cursor.to_list(length=query_fields.length)

        print('AQUI')
        print(documents)
        logger.info(SUCCESSFUL_GET_DOCUMENT)
        return documents

    async def add_document_to_db(self, document: Union[DogIn, UserIn]):
        """
        Se registra un nuevo documento en la base de datos.

        Parameters
        ----------
        document: Union[DogIn, UserIn]
            Información del documento a registrar.

        Returns
        -------
        out : Union[DogOut, UserOut].dict()
            Información del documento registrado.
        """
        logger.info(ADD_DOCUMENT)
        result = await database[self.collection].insert_one(document.dict())

        # Una vez registrado el documento (para obtener un ObjectId()) ya se
        # conoce el id y el tiempo de registro en base de datos, se actualiza
        # entonces estos campos en base de datos, solo si el documento es un
        # dog
        new_fields = {'ID': str(result.inserted_id)}
        if self.collection == 'dogs':
            new_fields['created_date'] = result.inserted_id.generation_time
        database[self.collection].update_one({'_id': result.inserted_id},
                                             {'$set': new_fields})

        query = QueryFields(ID=str(result.inserted_id))
        documents = await self.get_documents_from_db(query_fields=query)

        logger.info(SUCCESSFUL_ADD_DOCUMENT)
        return documents[0]

    async def add_document_to_db_celery(self, document: Union[DogIn, UserIn]):
        logger.info(ADD_DOCUMENT)
        result = add_document_to_database.delay(self.collection, document.dict())

        try:
            document = result.get()
        except:
            logger.error('FAILED TO ADD DOCUMENT TO DATABASE')

        logger.info(SUCCESSFUL_ADD_DOCUMENT)
        return document

    async def update_document_in_db(self, document: Union[DogIn, UserIn],
                                    query_fields: QueryFields = Depends()):
        """
        Se actualiza la información de algún documento en la base de datos.

        Parameters
        ----------
        document: Union[DogIn, UserIn]
            Información del documento a registrar.
        query_fields : QueryFields
            Clase cuyos atributos son los parámetros de búsqueda para el
            documento a actualizar, especificados por el usuario.

        Returns
        -------
        out : Union[DogOut, UserOut].dict()
            Información del documento actualizado.
        """
        logger.info(UPDATE_DOCUMENT)

        params = self.get_query_dict(query_fields)
        # Cuando un campo tiene None, es porque el usuario no quiere actualizar
        # dicho campo, por tanto se debe crear un diccionario de nuevos valores
        # que no los considere. No se puede cambiar el ID
        new_values = {key: value for (key, value) in document.dict().items()
                      if value is not None and key != 'ID'}

        # se debe esperar, pues la siguiente instrucción requiere que el campo ya
        # este actualizado y no una promesa de que se actualizara
        result = await database[self.collection].update_one(params, {'$set': new_values})

        if not result.raw_result['updatedExisting']:
            logger.error(FAILED_UPDATE_DOCUMENT)
            raise HTTPException(status_code=404, detail='Item not found while updating.')

        # los query_fields pueden haber cambiado en el proceso de actualización
        params.update(new_values)
        query_fields = QueryFields(**params)
        documents = await self.get_documents_from_db(query_fields=query_fields)

        logger.info(SUCCESSFUL_UPDATE_DOCUMENT)
        return documents[0]

    async def delete_document_in_db(self, query_fields: QueryFields = Depends()):
        """
        Se borra un documento de la base de datos.

        Parameters
        ----------
        query_fields : QueryFields
            Clase cuyos atributos son los parámetros de búsqueda para el
            documento a eliminar, especificados por el usuario.

        Returns
        -------
        out : Union[DogOut, UserOut].dict()
            Información del documento eliminado.
        """
        logger.info(DELETE_DOCUMENT)
        documents = await self.get_documents_from_db(query_fields=query_fields)
        if not documents:
            logger.error(FAILED_DELETE_DOCUMENT)
            raise HTTPException(status_code=404, detail='Item not found while deleting.')

        params = self.get_query_dict(query_fields)
        # el usuario no necesita esperar a que la coroutine se resuelva
        database[self.collection].delete_one(params)

        logger.info(SUCCESSFUL_DELETE_DOCUMENT)
        return documents[0]
