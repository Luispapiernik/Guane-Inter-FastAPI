from typing import Optional
from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]


# se crea esta clase por consistencia en los nombres
class UserIn(BaseUser):
    """
    Representación del modelo que se recibe del usuario al momento de registrar
    un nuevo user en la base de datos.
    """
    pass


class UserOut(BaseUser):
    """
    Representación del modelo que se le envía al usuario al momento de registrar
    o hacer una consulta de un user.
    """
    ID: str
