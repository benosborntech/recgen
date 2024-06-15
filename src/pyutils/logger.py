import logging
import sys


class Logger:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        self._info = logging.getLogger("info")
        self._error = logging.getLogger("error")
        self._fatal = logging.getLogger("fatal")

    def info(self, msg: str) -> None:
        self._info.info(msg)

    def error(self, msg: str) -> None:
        self._error.error(msg)

    def fatal(self, msg: str) -> None:
        self._fatal.fatal(msg)
        sys.exit(1)