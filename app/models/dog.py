import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class BaseDog(BaseModel):
    name: Optional[str]
    birth_date: Optional[datetime.datetime]
    picture: Optional[HttpUrl]
    is_adopted: Optional[bool]
    id_user: Optional[str]


# se crea esta clase por consistencia en los nombres
class DogIn(BaseDog):
    """
    Representación del modelo que se recibe del usuario al momento de registrar
    un nuevo dog en la base de datos.
    """
    pass


class DogOut(BaseDog):
    """
    Representación del modelo que se le envía al usuario al momento de registrar
    o hacer una consulta de un perro.
    """
    ID: str
    created_date: datetime.datetime
