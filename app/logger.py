import logging
from logging.config import dictConfig


log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s [%(asctime)s] - %(module)s: %(message)s',
            'datefmt': '%Y-%m-%d - %H:%M:%S',

        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'file': {
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'guane_inter_fastapi.log'
        }
    },
    'loggers': {
        'api-logger': {'handlers': ['default', 'file'], 'level': 'DEBUG'},
    },
}

logging.config.dictConfig(log_config)
logger = logging.getLogger('api-logger')
