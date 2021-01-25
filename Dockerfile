FROM python:3.9.1

WORKDIR /api

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app /api/app

ENV MONGO_HOST=mongo

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
