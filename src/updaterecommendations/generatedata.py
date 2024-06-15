import openai
import json

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

            cfg.get_logger().info(f"generating embeddings for '{key}'")

        f.seek(0)
        json.dump(data, f)

    cfg.get_logger().info(f"loaded {len(data.keys())} items")

    return data