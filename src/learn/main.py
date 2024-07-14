import redis
import kafka
import json
import os
import queue
import threading
import boto3

from src.pyutils.config import Config
from src.learn.loaddata import load_data
from src.pyutils.constants import EVENT_TOPIC
from src.learn.handler import handle


DATA_FILE = os.environ["DATA_FILE"]
REDIS_HOST = os.environ["REDIS_HOST"]
KAFKA_BROKER = os.environ["KAFKA_BROKER"]
SPACES_ENDPOINT_ORIGIN = os.environ["SPACES_ENDPOINT_ORIGIN"]
SPACES_ACCESS_KEY = os.environ["SPACES_ACCESS_KEY"]
SPACES_SECRET_KEY = os.environ["SPACES_SECRET_KEY"]
SPACE_NAME = os.environ["SPACE_NAME"]

def main() -> None:
    cfg = Config()

    r_client = redis.Redis(host=REDIS_HOST)
    k_consumer = kafka.KafkaConsumer(EVENT_TOPIC, bootstrap_servers=[KAFKA_BROKER], auto_offset_reset="earliest", enable_auto_commit=True)

    session = boto3.session.Session()
    client = session.client("s3", endpoint_url=SPACES_ENDPOINT_ORIGIN, aws_access_key_id=SPACES_ACCESS_KEY, aws_secret_access_key=SPACES_SECRET_KEY)

    q = queue.Queue()

    cfg.get_logger().info("initialized clients")

    data = load_data(cfg, DATA_FILE)

    cfg.get_logger().info("loaded data")

    thread = threading.Thread(target=handle, args=(cfg, r_client, q, client, SPACE_NAME, data))
    thread.daemon = True
    thread.start()

    cfg.get_logger().info("started daemon")

    for msg in k_consumer:
        body = json.loads(msg.value)

        cfg.get_logger().info(f"message body: '{body}'")

        q.put(body)

    thread.join()

if __name__ == "__main__":
    main()