from celery import Celery

app = Celery('app',
             broker='amqp://',
             backend='redis://')
