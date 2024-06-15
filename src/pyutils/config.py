import logger


class Config:
    def __init__(self) -> None:
        self.logger = logger.Logger()

    def get_logger(self) -> logger.Logger:
        return self.logger