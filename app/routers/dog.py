from typing import List, Optional
from fastapi import Depends, APIRouter

from ..models.dog import DogOut
from ..dependencies.database import *
from ..logger import logger

router = APIRouter()


@router.get('/dogs/', response_model=Optional[List[DogOut]])
def read_dogs(dogs: List[DogOut] = Depends(get_dogs_from_db)):
    logger.info('read_dogs')
    return dogs


@router.get('/dogs/{_id}')
def read_dog_by_id(dog: DogOut = Depends(get_dog_by_id)):
    logger.info('read_dog_by_id')
    return dog


@router.post('/dogs/')
def write_dog(dog: DogOut = Depends(add_dog_to_db)):
    logger.info('write_dog')
    return dog


@router.put('/dogs/{_id}')
def update_dog(dog: DogOut = Depends(update_dog_in_db)):
    logger.info('update_dog')
    return dog


@router.delete('/dogs/{_id}')
def delete_dog(dog: DogOut = Depends(delete_dog_from_db)):
    logger.info('delete_dog')
    return dog
