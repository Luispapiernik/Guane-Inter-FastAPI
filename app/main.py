from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse

from .logger import logger
from .logs.main_messages import *

from .models.security_models import *
from .dependencies.security import ACCESS_TOKEN_EXPIRE_MINUTES, users_database
from .dependencies.security import authenticate_user, create_access_token
from .routers import dog
from .routers import user


logger.info(INIT)
app = FastAPI()

logger.info(ROUTES)
app.include_router(dog.router)
app.include_router(user.router)


root_response = """<html>
    <head>
        <title>Guane Inter FastAPI</title>
    </head>
    <body>
        <h1>Hello World!!!</h1>
    </body>
</html>"""


@app.get('/', response_class=HTMLResponse)
async def root():
    logger.info(ROOT_POINT)
    return root_response


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(INIT_AUTHENTICATION)
    user = authenticate_user(users_database, form_data.username, form_data.password)
    if not user:
        logger.error(INCORRECT_USER_OR_PASSWORD)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    logger.info(CREATING_TOKEN)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    logger.info(SUCCESSFUL_AUTHENTICATION)
    return {"access_token": access_token, "token_type": "bearer"}
