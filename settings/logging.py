# Service uses local_logging.py for logging configuration if available. Otherwise, it uses logging.py.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
        "file": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        #        'file': {
        #            'class': 'logging.FileHandler',
        #            'filename': 'production.log',
        #            'formatter': 'file',
        #        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
        "registry": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
