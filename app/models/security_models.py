from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """
    Esta clase representa la respuesta que se le da al usuario cuando se autentica
    con credenciales validas para obtener un token
    """
    access_token: str
    token_type: str


# se define para aprovechar la ayuda que ofrecen los IDEs
class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    """
    Esta clase representa el modelo del usuario (administrador) que se usa
    internamente en las funciones
    """
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    """
    Esta clase representa el modelo del usuario (administrador) que se almacena
    en base de datos
    """
    hashed_password: str
