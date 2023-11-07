import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import configuration


class Logger:
    child_logger_registration = {}
    loggers = []

    def __init__(self, log_name: str, child_loggers=None):

        if child_loggers is None:
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
            self.child_loggers = None
            Logger.loggers.append(self.logger)
        else:
            self.name = log_name
            self.child_loggers = child_loggers

    def is_child_logger(self):
        return bool(self.child_loggers)

    def _check_for_unregistered_loggers(self):
        for parent_logger in Logger.loggers:
            if parent_logger not in Logger.child_logger_registration[self.logger.name]:
                child_logger = logging.getLogger(f"{parent_logger.name}.{self.logger.name}")
                self.child_loggers.append(child_logger)
                Logger.child_logger_registration[self.logger.name].append(parent_logger)

    def log(self, level, *args, **kwargs):
        if self.is_child_logger():
            self._log_to_child(level, *args)
        else:
            self._log_to_parent(level, *args)

    def _log_to_child(self, level, *args):
        self._check_for_unregistered_loggers()
        for logger in self.child_loggers:
            getattr(logger, level)(*args)

    @staticmethod
    def _log_to_parent(level, *args):
        for parent_logger in Logger.loggers:
            getattr(parent_logger, level)(*args)

    def debug(self, *args):
        self.log('debug', *args)

    def info(self, *args):
        self.log('info', *args)

    def warning(self, *args):
        self.log('warning', *args)

    def error(self, *args):
        self.log('error', *args)

    def exception(self, *args, **kwargs):
        self.log('error', *args, **kwargs)

    @classmethod
    def get_child_logger(cls, log_name: str):
        child_loggers = []
        for parent_logger in Logger.loggers:
            child_logger = logging.getLogger(f"{parent_logger.name}.{log_name}")
            child_loggers.append(child_logger)
            Logger.child_logger_registration.setdefault(log_name, []).append(parent_logger)
        return cls(log_name, child_loggers=child_loggers)
