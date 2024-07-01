import redis
import kafka
import json
import os
import queue
import threading

from src.pyutils.config import Config
from src.pyutils.constants import EVENT_TOPIC
from src.updaterecommendations.handler import handle


REDIS_HOST = os.environ["REDIS_HOST"]
KAFKA_BROKER = os.environ["KAFKA_BROKER"]

def main() -> None:
    cfg = Config()

    r_client = redis.Redis(host=REDIS_HOST)
    k_consumer = kafka.KafkaConsumer(EVENT_TOPIC, bootstrap_servers=[KAFKA_BROKER], auto_offset_reset="earliest", enable_auto_commit=True)

    cfg.get_logger().info("initialized clients")

    q = queue.Queue()

    thread = threading.Thread(target=handle, args=(cfg, r_client, q))
    thread.daemon = True
    thread.start()

    for msg in k_consumer:
        body = json.loads(msg.value)

        cfg.get_logger().info(f"message body: '{body}'")

        q.put(body)

    thread.join()

if __name__ == "__main__":
    main()