from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from ..models.dog import DogIn

client = AsyncIOMotorClient('localhost', 27017)
database = client.guane_inter_fast_api


async def get_dogs_from_db(number_of_dogs: Optional[int] = 1):
    cursor = database.dogs.find({})
    dogs = await cursor.to_list(length=number_of_dogs)

    return dogs


async def get_dog_by_id(_id: str):
    dog = await database.dogs.find_one({'id': _id})
    del dog['_id']

    return dog


async def add_dog_to_db(dog: DogIn):
    result = await database.dogs.insert_one(dog.dict())

    new_fields = {'created_date': result.inserted_id.generation_time,
                  'id': str(result.inserted_id)}
    database.dogs.update_one({'_id': result.inserted_id},
                             {'$set': new_fields})

    dog = await get_dog_by_id(str(result.inserted_id))
    return dog


async def update_dog_in_db(_id: str, dog: DogIn):
    new_values = {key: value for (key, value) in dog.dict().items()
                  if value is not None}
    result = await database.dogs.update_one({'id': _id}, {'$set': new_values})

    dog = await get_dog_by_id(_id)
    return dog


async def delete_dog_from_db(_id: str):
    dog = await get_dog_by_id(_id)

    database.dogs.delete_one({'id': _id})

    return dog
