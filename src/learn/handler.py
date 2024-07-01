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

            # **** Here we need to actually train the model - for this we are going to need to do some data processing to transform the inputs into what we need them to be
            # **** Now I need a daemon thread here which will acquire the lock, train the model from a given amount of selections every few seconds, and then save the files to S3

            # **** We will need to save our weights to some file
            # **** Then we will have to upload the model with the same name - we can just override we don't really care that much about checkpoints and it doesnt matter what the previous one reads, we can just switch it out in RAM every few minutes...

        lock.release()

        cfg.get_logger().info(f"released lock {k_lock}")