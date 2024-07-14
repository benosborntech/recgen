import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import redis
import queue
import time
import os

from src.pyutils.config import Config
from src.pyutils.constants import TRAIN_TIMEOUT, TRAIN_BATCH_SIZE, LOCK_PREFIX, LOCK_TIMEOUT, LOCK_UNIQUE_ID, LOCK_ID_LEARN, MODEL_FILE_NAME, MODEL_EMBEDDING_SIZE, MODEL_LEARNING_RATE, MODEL_EPOCHS
from src.pyutils.keyconcat import key_concat
from src.pyutils.model import Body, Data
from src.pyutils.nn import RecommendationModel, RecommendationDataset


LOCAL_FILE = os.path.join("/tmp", MODEL_FILE_NAME)

def handle(cfg: Config, r_client: redis.Redis, queue: queue.Queue, client: any, space_name: str, data: Data) -> None:
    while True:
        time.sleep(TRAIN_TIMEOUT)

        k_lock = key_concat(LOCK_PREFIX, LOCK_UNIQUE_ID, LOCK_ID_LEARN)
        lock = r_client.lock(k_lock, LOCK_TIMEOUT)
        lock.acquire(blocking=True)

        cfg.get_logger().info(f"acquired lock {k_lock}")

        batch: list[Body] = []
        while not queue.empty() and len(batch) < TRAIN_BATCH_SIZE:
            elem = queue.get()

            batch.append(elem)

        if len(batch) > 0:
            cfg.get_logger().info("batch size is non empty - proceeding")

            # Load the model from the file
            client.download_file(space_name, MODEL_FILE_NAME, LOCAL_FILE)
            model = RecommendationModel(MODEL_EMBEDDING_SIZE)

            with open(LOCAL_FILE, "r") as f:
                data = f.read()
                model.load_state_dict(data)

            cfg.get_logger().info("loaded current model")

            # Add user embeddings if they do not yet exist
            for item in batch:
                user_id = item["userId"]

                if not model.user_exists(user_id):
                    model.add_user(user_id)

                    cfg.get_logger().info(f"added embeddings for {user_id}")

            cfg.get_logger().info("added new user embeddings")

            # Train the model
            criterion = nn.BCELoss()
            optimizer = optim.Adam(model.parameters(), lr=MODEL_LEARNING_RATE)

            dataset = RecommendationDataset(batch, MODEL_EMBEDDING_SIZE)
            dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

            for epoch in range(MODEL_EPOCHS):
                cfg.get_logger().info(f"beginning epoch {epoch}")

                for user_id, item_emb, label in dataloader:
                    output = model(user_id, item_emb)
                    loss = criterion(output, label)

                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

            # Serialize and save the model
            with open(LOCAL_FILE, "w") as f:
                data = model.state_dict ()
                f.write(data)
                
            client.upload_file(LOCAL_FILE, space_name, MODEL_FILE_NAME)

            cfg.get_logger().info("saved updated model")

        lock.release()

        cfg.get_logger().info(f"released lock {k_lock}")