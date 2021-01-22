from typing import List, Optional
from fastapi import Depends, APIRouter

from ..logger import logger
from ..logs.users_messages import *

from ..models.user import UserOut
from ..dependencies.database import DatabaseManager
from ..dependencies.security import get_current_active_user, User


router = APIRouter()
database = DatabaseManager('users')


@router.get('/users/', response_model=Optional[List[UserOut]])
async def read_users(users: List[UserOut] = Depends(database.get_documents_from_db)):
    logger.info(READ_USER)
    return users


@router.post('/users/', response_model=Optional[UserOut])
async def write_user(user: UserOut = Depends(database.add_document_to_db),
                     current_user: User = Depends(get_current_active_user)):
    logger.info(WRITE_USER)
    return user


@router.put('/users/', response_model=Optional[UserOut])
async def update_user(user: UserOut = Depends(database.update_document_in_db),
                      current_user: User = Depends(get_current_active_user)):
    logger.info(UPDATE_USER)
    return user


@router.delete('/users/', response_model=Optional[UserOut])
async def delete_user(user: UserOut = Depends(database.delete_document_in_db)):
    logger.info(DELETE_USER)
    return user
