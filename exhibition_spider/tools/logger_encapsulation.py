import logging
from config import logger_config

logging.basicConfig(**logger_config)


class Logger:
    def __init__(self):
        pass

    def info(self, massage):
        logging.info(massage)

    def warnning(self, massage):
        logging.warning(massage)

    def error(self, massage):
        logging.error(massage)
