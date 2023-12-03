import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import configuration
from collections import defaultdict


class Logger:
    child_logger_registration = defaultdict(list)
    logger = None

    def __init__(self, log_name: str, child_logger=False):

        if not child_logger:
            self.logger = logging.getLogger(log_name)
            self.logger.setLevel(logging.DEBUG)

            logs_folder = Path(f"{configuration.ROOT_PATH}/logs")
            logs_folder.mkdir(exist_ok=True)
            log_file = f"{configuration.ROOT_PATH}/logs/{log_name}.log"

            log_handler = TimedRotatingFileHandler(log_file, when='midnight', utc=True, encoding='utf-8')

            log_formatter = logging.Formatter(
                '%(asctime)s - %(process)s - %(thread)s - %(name)s - %(levelname)s - %(message)s'
            )
            log_handler.setFormatter(log_formatter)
            self.logger.addHandler(log_handler)
            self.child_logger = False
            Logger.logger = self.logger
        else:
            self.name = log_name
            self.child_logger = child_logger

    def register_parent_logger(self):
        parent_logger = Logger.logger
        if parent_logger and parent_logger not in Logger.child_logger_registration[self.name]:
            self.child_logger = logging.getLogger(f"{parent_logger.name}.{self.name}")
            Logger.child_logger_registration[self.name].append(parent_logger)

    def _log(self, level, *args, **kwargs):
        if self.child_logger:
            self.register_parent_logger()
            getattr(self.child_logger, level)(*args)
        else:
            if not Logger.logger:
                Logger('undefined')
            getattr(Logger.logger, level)(*args)

    def debug(self, *args):
        self._log('debug', *args)

    def info(self, *args):
        self._log('info', *args)

    def warning(self, *args):
        self._log('warning', *args)

    def error(self, *args):
        self._log('error', *args)

    def exception(self, *args, **kwargs):
        self._log('error', *args, **kwargs)

    @classmethod
    def get_child_logger(cls, log_name: str):
        return cls(log_name, child_logger=True)


UVICORN_LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'format': '%(asctime)s - %(process)s - %(thread)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        "error_default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr"
        },
        'error_file_handler': {
            'formatter': 'default',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            "filename": "logs/uvicorn_error.log",
            "when": 'midnight',
            "utc": True,
            "encoding": 'utf-8'
        },
        'access_handler': {
            'formatter': 'default',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            "filename": "logs/uvicorn_access.log",
            "when": 'midnight',
            "utc": True,
            "encoding": 'utf-8'
        },
    },
    'loggers': {
        'uvicorn.error': {
            'level': 'INFO',
            'handlers': ['error_file_handler', 'error_default'],
            'propagate': False
        },
        'uvicorn.access': {
            'level': 'INFO',
            'handlers': ['access_handler'],
            'propagate': False
        },
    }
}
