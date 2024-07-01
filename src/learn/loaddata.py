import json

from src.pyutils.model import Data
from src.pyutils.config import Config


def load_data(cfg: Config, file: str) -> Data:
    with open(file, "r+") as f:
        data = json.load(f)

    cfg.get_logger().info(f"loaded {len(data.keys())} items")

    return data