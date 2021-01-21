from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from ..models.dog import DogIn

# por defecto mongo inicia su servicio en el puerto 27017, si se quiere cambiar
# este numero se debe forzar a lanzar el servicio por otro puerto
client = AsyncIOMotorClient('localhost', 27017)
database = client.guane_inter_fast_api


async def get_dogs_from_db(number_of_dogs: Optional[int] = 1):
    """
    Se consultan la información de los documentos que estan registrados en la
    base de datos

    Parameters
    ----------
    number_of_dogs : int
        Maximo numero de documentos a consultar

    Returns
    -------
    out : List[DogOut.dict()]
        Lista con la información del numero dado de documentos
    """
    cursor = database.dogs.find({})

    # no se puede retornar una coroutine porque FastApi aplica una conversion
    # sobre los resultados que retornan las dependencias para pasarlos a
    # las path functions
    dogs = await cursor.to_list(length=number_of_dogs)

    return dogs


async def get_dog_by_id(_id: str):
    """
    Se consulta la información de un documento de acuerdo al id

    Parameters
    ----------
    _id : str
        id con el que se registro el documento en la base de datos

    Returns
    -------
    out : DogOut.dict()
        Información de un documento dado
    """
    dog = await database.dogs.find_one({'id': _id})

    # Este campo lo agrega mongo al momento de registrar un nuevo documento
    # el usuario no necesita verlo
    del dog['_id']

    return dog


async def add_dog_to_db(dog: DogIn):
    """
    Se registra un nuevo documento en base de datos

    Parameters
    ----------
    dog : DogIn
        Información del documento a registrar

    Returns
    -------
    out : DogOut.dict()
        Información del documento registrado. Se tienen campos nuevos, para
        tiempo de creación del registro y el id en la base de datos
    """
    result = await database.dogs.insert_one(dog.dict())

    # Una vez registrado (para obtener un ObjectId()) ya se conoce el id
    # y el tiempo de registro en base de datos, se actualiza entonces estos
    # campos en base de datos
    new_fields = {'created_date': result.inserted_id.generation_time,
                  'id': str(result.inserted_id)}
    database.dogs.update_one({'_id': result.inserted_id},
                             {'$set': new_fields})

    dog = await get_dog_by_id(str(result.inserted_id))
    return dog


async def update_dog_in_db(_id: str, dog: DogIn):
    """
    Se actualiza la información de algún documento en la base de datos

    Parameters
    ----------
    _id : str
        id del documento a actualizar
    dog : DogIn
        Información a actualizar

    Returns
    -------
    out : DogOut.dict()
        información del documento actualizado
    """
    # Cuando un campo tiene None, es porque el usuario no quiere actualizar
    # dicho campo, por tanto se debe crear un diccionario de nuevos valores
    # que no los considere
    new_values = {key: value for (key, value) in dog.dict().items()
                  if value is not None}

    # se debe esperar, pues la siguiente instrucción requiere que el campo ya
    # este actualizado y no una promesa de que se actualizara
    await database.dogs.update_one({'id': _id}, {'$set': new_values})

    dog = await get_dog_by_id(_id)
    return dog


async def delete_dog_from_db(_id: str):
    """
    Se borra un documento de la base de datos

    Parameters
    ----------
    _id : str
        id del documento a borrar

    Returns
    -------
    out : DogOut.dict()
        Información del documento eliminado
    """
    dog = await get_dog_by_id(_id)

    # el usuario no necesita esperar a que la coroutine se resuelva
    database.dogs.delete_one({'id': _id})
    return dog
