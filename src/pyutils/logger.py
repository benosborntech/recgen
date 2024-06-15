import logging
import sys


class Logger:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        self.info = logging.getLogger('info')
        self.error = logging.getLogger('error')
        self.fatal = logging.getLogger('fatal')

    def info(self, msg: str) -> None:
        self.info.info(msg)

    def error(self, msg: str) -> None:
        self.error.error(msg)

    def fatal(self, msg: str) -> None:
        self.fatal.fatal(msg)
        sys.exit(1)