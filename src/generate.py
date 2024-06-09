import openai
import os
import json

client = openai.OpenAI(
    api_key=os.environ["OPENAI_KEY"]
)

FILE = "data.json"

def main():
    with open(FILE, "r+") as f:
        data = json.load(f)

        for key, value in data.items():
            description = value["description"]

            response = client.embeddings.create(input=description, model="text-embedding-ada-002")
            embeddings = response.data[0].embedding

            data[key]["vector"] = embeddings

        f.seek(0)
        json.dump(data, f)

main()