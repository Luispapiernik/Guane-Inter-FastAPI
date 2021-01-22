from typing import List, Optional
from fastapi import Depends, APIRouter

from ..logger import logger
from ..models.user import UserOut
from ..dependencies.database import DatabaseManager


router = APIRouter()
database = DatabaseManager('users')


@router.get('/users/', response_model=Optional[List[UserOut]])
async def read_users(users: List[UserOut] = Depends(database.get_documents_from_db)):
    logger.info('read_users')
    return users


@router.post('/users/', response_model=Optional[UserOut])
async def write_user(user: UserOut = Depends(database.add_document_to_db)):
    logger.info('write_user')
    return user


@router.put('/users/', response_model=Optional[UserOut])
async def update_user(user: UserOut = Depends(database.update_document_in_db)):
    logger.info('update_user')
    return user


@router.delete('/users/', response_model=Optional[UserOut])
async def delete_user(user: UserOut = Depends(database.delete_document_in_db)):
    logger.info('delete_user')
    return user
