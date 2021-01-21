from fastapi import FastAPI
from .logger import logger

from .routers import dog


logger.info('Instantiating the API')
app = FastAPI()

logger.info('Setting routes')
app.include_router(dog.router)


@app.get('/')
def root():
    logger.info('root')
    return {'message': 'Hello World!!!'}
