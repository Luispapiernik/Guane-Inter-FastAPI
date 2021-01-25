from celery import Celery
import os

# RABBIT_HOST = os.getenv('RABBIT_HOST', 'rabbitmq')
# REDIS_HOST = os.getenv('REDIS_HOST', 'redis')

RABBIT_HOST = os.getenv('RABBIT_HOST', 'localhost')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')

app = Celery('tasks',
             broker='amqp://%s:5672' % RABBIT_HOST,
             backend='redis://%s:6379' % REDIS_HOST)
