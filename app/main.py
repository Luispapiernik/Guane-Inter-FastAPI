from fastapi import FastAPI

from .routers import dog

app = FastAPI()
app.include_router(dog.router)


@app.get('/')
def root():
    return {'message': 'Hello World!!!'}
