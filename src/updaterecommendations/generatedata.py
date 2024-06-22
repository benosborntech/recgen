import openai
import json
import numpy as np

from src.pyutils.model import Data
from src.pyutils.config import Config


def generate_data(cfg: Config, file: str, oai_client: openai.OpenAI) -> Data:
    with open(file, "r+") as f:
        data = json.load(f)

        for key, value in data.items():
            if len(data[key]["vector"]) > 0:
                continue

            description = value["description"]

            response = oai_client.embeddings.create(input=description, model="text-embedding-ada-002")
            embeddings = response.data[0].embedding

            data[key]["vector"] = embeddings

            cfg.get_logger().info(f"generated embeddings for '{key}'")

        f.seek(0)
        json.dump(data, f)

    cfg.get_logger().info(f"loaded {len(data.keys())} items")

    for key, value in data.items():
        data[key]["vector"] = np.array(value["vector"], dtype=np.float32)

    cfg.get_logger().info(f"converted to np array")

    return data