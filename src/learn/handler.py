import redis
import queue
import time

from src.pyutils.config import Config
from src.pyutils.constants import TRAIN_TIMEOUT, TRAIN_BATCH_SIZE, LOCK_PREFIX, LOCK_TIMEOUT, LOCK_UNIQUE_ID, LOCK_ID_LEARN
from src.pyutils.keyconcat import key_concat
from src.pyutils.model import Body


def handle(cfg: Config, r_client: redis.Redis, queue: queue.Queue, client: any) -> None:
    while True:
        time.sleep(TRAIN_TIMEOUT)

        k_lock = key_concat(LOCK_PREFIX, LOCK_UNIQUE_ID, LOCK_ID_LEARN)
        lock = r_client.lock(k_lock, LOCK_TIMEOUT)
        lock.acquire(blocking=True)

        cfg.get_logger().info(f"acquired lock {k_lock}")

        batch: list[Body] = []
        while len(queue) > 0 and len(batch) < TRAIN_BATCH_SIZE:
            elem = queue.get()

            batch.append(elem)

        if len(batch) > 0:
            cfg.get_logger().info("batch size is non empty - proceeding")

            # Load the model from the file

            # Add user embeddings if they do not yet exist

            # Convert the data to the right format and create the batch

            # Train the model

            # Serialize and save the model

        lock.release()

        cfg.get_logger().info(f"released lock {k_lock}")