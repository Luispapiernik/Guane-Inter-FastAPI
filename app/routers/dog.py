from typing import List, Optional
from fastapi import Depends, APIRouter

from ..logger import logger
from ..models.dog import DogOut
from ..dependencies.database import DatabaseManager


router = APIRouter()
database = DatabaseManager('dogs')


@router.get('/dogs/', response_model=Optional[List[DogOut]])
async def read_dogs(dogs: List[DogOut] = Depends(database.get_documents_from_db)):
    logger.info('read_dogs')
    return dogs


@router.post('/dogs/', response_model=Optional[DogOut])
async def write_dog(dog: DogOut = Depends(database.add_document_to_db)):
    logger.info('write_dog')
    return dog


@router.put('/dogs/', response_model=Optional[DogOut])
async def update_dog(dog: DogOut = Depends(database.update_document_in_db)):
    logger.info('update_dog')
    return dog


@router.delete('/dogs/', response_model=Optional[DogOut])
async def delete_dog(dog: DogOut = Depends(database.delete_document_in_db)):
    logger.info('delete_dog')
    return dog
