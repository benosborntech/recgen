from src.pyutils.logger import Logger


class Config:
    def __init__(self) -> None:
        self.logger = Logger()

    def get_logger(self) -> Logger:
        return self.logger