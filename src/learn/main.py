import redis
import kafka
import json
import os
import queue
import threading
import boto3

from src.pyutils.config import Config
from src.pyutils.constants import EVENT_TOPIC
from src.learn.handler import handle


REDIS_HOST = os.environ["REDIS_HOST"]
KAFKA_BROKER = os.environ["KAFKA_BROKER"]
SPACES_ENDPOINT = os.environ["SPACES_ENDPOINT"]
SPACES_REGION = os.environ["SPACES_REGION"]
SPACES_ACCESS_KEY = os.environ["SPACES_ACCESS_KEY"]
SPACES_SECRET_KEY = os.environ["SPACES_SECRET_KEY"]
SPACE_NAME = os.environ["SPACE_NAME"]

def main() -> None:
    cfg = Config()

    r_client = redis.Redis(host=REDIS_HOST)
    k_consumer = kafka.KafkaConsumer(EVENT_TOPIC, bootstrap_servers=[KAFKA_BROKER], auto_offset_reset="earliest", enable_auto_commit=True)

    session = boto3.session.Session()
    client = session.client("s3", region_name=SPACES_REGION, endpoint_url=SPACES_ENDPOINT, aws_access_key_id=SPACES_ACCESS_KEY, aws_secret_access_key=SPACES_SECRET_KEY)

    cfg.get_logger().info("initialized clients")

    q = queue.Queue()

    thread = threading.Thread(target=handle, args=(cfg, r_client, q, client, SPACE_NAME))
    thread.daemon = True
    thread.start()

    for msg in k_consumer:
        body = json.loads(msg.value)

        cfg.get_logger().info(f"message body: '{body}'")

        q.put(body)

    thread.join()

if __name__ == "__main__":
    main()