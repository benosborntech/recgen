import os
import openai
import redis
import kafka
import json

from src.pyutils.config import Config
from src.pyutils.constants import EVENT_TOPIC
from src.updaterecommendations.generatedata import generate_data
from src.updaterecommendations.loaddata import load_data
from src.updaterecommendations.handler import handle


DATA_FILE = os.environ["DATA_FILE"]
REDIS_ADDR = os.environ["REDIS_ADDR"]
KAFKA_BROKER = os.environ["KAFKA_BROKER"]
OPENAI_KEY = os.environ["OPENAI_KEY"]

def main() -> None:
    cfg = Config()

    oai_client = openai.OpenAI(api_key=OPENAI_KEY)
    r_client = redis.Redis(host=REDIS_ADDR)
    k_consumer = kafka.KafkaConsumer(EVENT_TOPIC, bootstrap_servers=[KAFKA_BROKER])

    cfg.get_logger().info("initialized clients")

    data = generate_data(cfg, DATA_FILE, oai_client)
    load_data(cfg, r_client, data)

    cfg.get_logger().info("loaded data")

    for msg in k_consumer:
        body = json.loads(msg.value)

        cfg.get_logger().info(f"message body: '{body}'")

        handle(cfg, r_client, body)

main()