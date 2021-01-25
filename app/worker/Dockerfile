FROM python:3.9.1

WORKDIR /api

COPY . /api/app/worker

RUN pip install -r ./app/worker/requirements.txt

CMD ["celery", "-A", "app.worker.tasks", "worker", "--loglevel=INFO"]
