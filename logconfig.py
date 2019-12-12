# -*- coding: utf-8 -*-
import logging.config


LOG_SETTINGS = {
    'version': 1,
    'root': {
        'level': 'DEBUG',
        'handlers': ['file'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple'
        },
        'file': {
            'class' : 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': 'ulisp_swank.log'
        },
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s: %(module)s:%(lineno)s. %(message)s',
        },
    },
}

# try:
#     from local_logconfig import configure
# except ImportError:
def configure():
    logging.config.dictConfig(LOG_SETTINGS)
