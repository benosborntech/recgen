import os
import openai
import redis
import kafka
import json
import boto3
import torch

from src.pyutils.config import Config
from src.pyutils.constants import EVENT_TOPIC, MODEL_FILE_NAME, MODEL_EMBEDDING_SIZE
from src.updaterecommendations.generatedata import generate_data
from src.updaterecommendations.loaddata import load_data
from src.updaterecommendations.handler import handle
from src.pyutils.nn import RecommendationModel


LOCAL_FILE = os.path.join("/tmp", MODEL_FILE_NAME)

DATA_FILE = os.environ["DATA_FILE"]
REDIS_HOST = os.environ["REDIS_HOST"]
KAFKA_BROKER = os.environ["KAFKA_BROKER"]
OPENAI_KEY = os.environ["OPENAI_KEY"]
SPACES_ENDPOINT_ORIGIN = os.environ["SPACES_ENDPOINT_ORIGIN"]
SPACES_ACCESS_KEY = os.environ["SPACES_ACCESS_KEY"]
SPACES_SECRET_KEY = os.environ["SPACES_SECRET_KEY"]
SPACE_NAME = os.environ["SPACE_NAME"]

def main() -> None:
    cfg = Config()

    oai_client = openai.OpenAI(api_key=OPENAI_KEY)
    r_client = redis.Redis(host=REDIS_HOST)
    k_consumer = kafka.KafkaConsumer(EVENT_TOPIC, bootstrap_servers=[KAFKA_BROKER], auto_offset_reset="earliest", enable_auto_commit=True)

    session = boto3.session.Session()
    client = session.client("s3", endpoint_url=SPACES_ENDPOINT_ORIGIN, aws_access_key_id=SPACES_ACCESS_KEY, aws_secret_access_key=SPACES_SECRET_KEY)

    cfg.get_logger().info("initialized clients")

    data = generate_data(cfg, DATA_FILE, oai_client)
    load_data(cfg, r_client, data)

    cfg.get_logger().info("loaded data")

    for msg in k_consumer:
        body = json.loads(msg.value)

        cfg.get_logger().info(f"message body: '{body}'")

        model = RecommendationModel(MODEL_EMBEDDING_SIZE)

        try:
            client.download_file(SPACE_NAME, MODEL_FILE_NAME, LOCAL_FILE)
            model.load_state_dict(torch.load(LOCAL_FILE))

            cfg.get_logger().info("loaded current model")
        except Exception as e:
            cfg.get_logger().info(f"failed to load existing model for reason - using new model: {e}")

        handle(cfg, r_client, body, model)

if __name__ == "__main__":
    main()