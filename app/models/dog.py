from typing import Optional
import datetime
from pydantic import BaseModel, HttpUrl


class BaseDog(BaseModel):
    name: Optional[str]
    birth_date: Optional[datetime.datetime]
    picture: Optional[HttpUrl]
    is_adopted: Optional[bool]


class DogIn(BaseDog):
    pass


class DogOut(BaseDog):
    id: str
    created_date: datetime.datetime
