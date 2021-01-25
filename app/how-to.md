# Como configurar el servicio docker

## se crean las imagenes y se inicia el contenedor de mongo
sudo docker-compose up -d

## Se inicia el contenedor de fastapi
sudo docker run -p 8000:80  guane-inter-fastapi_web


## Se abre terminal del contenedor db
sudo docker-compose exec db bash

## run celery in the same directory that uvicorn
celery -A app.worker.tasks worker --loglevel=INFO