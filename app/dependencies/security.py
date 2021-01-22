from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..logger import logger
from ..logs.security_messages import *
from ..models.security_models import *

# openssl rand -hex 32
SECRET_KEY = "7c4b24b47e6db890b03642a5cf51a3b7530c841c3dd2d80ccf49e976d20444a5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


users_database = {
    "Luispapiernik": {
        "username": "Luispapiernik",
        "full_name": "Luis Papiernik",
        "email": "lpapiernik24@gmail.com",
        "hashed_password": "$2b$12$Jp3lIMSzaQy9H40Lxl9xm.lzo.LU51X95xHXUMkDEBlBmoAvcnEvC",
        "disabled": False,
    }
}


logger.info(CRYPT_CONTEXT)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """
    Se verifica que el hash de plain_password coincida con el valor
    hashed_password.

    Parameters
    ----------
    plain_password : str
        Contraseña a la que se le va a verificar el hash.
    hashed_password : str
        Hash usado para la verificación.

    Returns
    -------
    out : bool
        True en caso de que los valores coincidan, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Se calcula el hash de un string

    Parameters
    ----------
    password : str
        Texto al que se le calculara el hash.

    Returns
    -------
    out : str
        String con el hash correspondiente al texto.
    """
    return pwd_context.hash(password)


def get_user(database, username: str):
    """
    Esta función retorna un usuario de la base de datos.

    Parameters
    ----------
    database : dict
        La base de datos representada como un diccionario, donde las claves
        son los usernames.
    username : str
        Usuario que se quiere extraer de la base de datos.

    Returns
    -------
    out : UserInDB, None
        Datos del usuario.
    """
    if username in database:
        user_dict = database[username]
        return UserInDB(**user_dict)


def authenticate_user(database, username: str, password: str):
    """
    Se verifica que el usuario pasado como parámetro este en base de datos y
    tenga correctas las credenciales.

    Parameters
    ----------
    database : dict
        Base de datos representada como un diccionario.
    username : str
        username del usuario a verificar
    password : str
        contraseña del usuario (texto plano) a verificar.

    Returns
    -------
    out : bool
        True en caso de que la autenticación haya sido exitosa, False en caso
        contrario.
    """
    user = get_user(database, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Se crea un token de acceso.

    Parameters
    ----------
    data : dict
        Diccionario que puede corresponder a datos de un usuario.
    expires_delta : timedelta
        Tiempo de validez del token.

    Returns
    -------
    out : str
        Token de acceso.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Se obtiene el usuario asociado a un token

    Parameters
    ----------
    token : str
        Token para el que se rastreara a que usuario pertenece.

    Returns
    -------
    out : UserInDB
        Usuario asociado al token.
    """
    logger.info(GET_TOKEN)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            logger.error(NOT_VALIDATE)
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        logger.error(NOT_VALIDATE)
        raise credentials_exception
    user = get_user(users_database, username=token_data.username)
    if user is None:
        logger.error(NOT_VALIDATE)
        raise credentials_exception

    logger.info(SUCCESSFUL_RECUPERATION)
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Se verifica si un usuario tiene un token activo

    Parameters
    ----------
    current_user : User
        Usuario al que se le hara la verificación

    Returns
    -------
    out: User
        En caso de que la verificación falle no se retorna al usuario, en cambio
        se lanza una excepción
    """
    logger.info(CHECK_USER)
    if current_user.disabled:
        logger.error(INACTIVE_USER)
        raise HTTPException(status_code=400, detail='Inactive user')
    logger.info(ACTIVE_USER)
    return current_user
