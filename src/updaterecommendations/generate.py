import openai
import json
from ..pyutils.model import Data

def generate_data(file: str, client: openai.OpenAI) -> Data:
    with open(file, "r+") as f:
        data = json.load(f)

        for key, value in data.items():
            description = value["description"]

            response = client.embeddings.create(input=description, model="text-embedding-ada-002")
            embeddings = response.data[0].embedding

            data[key]["vector"] = embeddings

        f.seek(0)
        json.dump(data, f)

    return data