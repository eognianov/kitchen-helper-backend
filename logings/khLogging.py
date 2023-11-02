import os
import logging
from logging.handlers import TimedRotatingFileHandler


class Logger:
    def __init__(self, name, log_level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] - %(message)s')

        log_folder = os.path.join(os.getcwd(), "logs")

        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        log_file = os.path.join(log_folder, f"{name}.log")
        handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def get_child(self, name):
        return self.logger.getChild(name)


if __name__ == "__main__":
    root_logger = Logger("root_logger")
    child_logger = root_logger.get_child("child_logger")

    root_logger.logger.debug("This is a debug message in the root logger.")
    child_logger.info("This is an info message in the child logger.")
