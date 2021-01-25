from typing import List, Optional
from fastapi import Depends, APIRouter

from ..logger import logger
from ..logs.dogs_messages import *

from ..models.dog import DogOut
from ..dependencies.database import DatabaseManager
from ..dependencies.security import get_current_active_user, User


router = APIRouter()
database = DatabaseManager('dogs')


@router.get('/dogs/', response_model=List[Optional[DogOut]])
async def read_dogs(dogs: List[Optional[DogOut]] = Depends(database.get_documents_from_db)):
    logger.info(READ_DOGS)
    return dogs


@router.post('/dogs/', response_model=Optional[DogOut])
async def write_dog(dog: DogOut = Depends(database.add_document_to_db),
                    current_user: User = Depends(get_current_active_user)):
    logger.info(WRITE_DOGS)
    return dog


@router.post('/concurrently/dogs/', response_model=Optional[DogOut])
async def write_dog_concurrently(dog: DogOut = Depends(database.add_document_to_db_celery),
                                 current_user: User = Depends(get_current_active_user)):
    logger.info(WRITE_DOGS)
    return dog


@router.put('/dogs/', response_model=Optional[DogOut])
async def update_dog(dog: DogOut = Depends(database.update_document_in_db),
                     current_user: User = Depends(get_current_active_user)):
    logger.info(UPDATE_DOGS)
    return dog


@router.delete('/dogs/', response_model=Optional[DogOut])
async def delete_dog(dog: DogOut = Depends(database.delete_document_in_db)):
    logger.info(DELETE_DOGS)
    return dog
