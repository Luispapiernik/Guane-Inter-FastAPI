from fastapi import FastAPI
from .logger import logger

from .routers import dog
from .routers import user


logger.info('Instantiating the API')
app = FastAPI()

logger.info('Setting routes')
app.include_router(dog.router)
app.include_router(user.router)


@app.get('/')
def root():
    logger.info('root')
    return {'message': 'Hello World!!!'}
