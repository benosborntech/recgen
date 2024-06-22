import redis
from redis.commands.search.indexDefinition import (
    IndexDefinition,
    IndexType
)
from redis.commands.search.query import Query
from redis.commands.search.field import (
    TextField,
    VectorField
)

from src.pyutils.model import Data
from src.pyutils.keyconcat import key_concat
from src.pyutils.constants import VECTOR_INDEX, DB_HASH_PREFIX
from src.pyutils.config import Config


def load_data(cfg: Config, r_client: redis.Redis, data: Data) -> None:
    values = data.values()
    vec_len = len(values)
    vec_dim = len(list(values)[0]["vector"])

    id = TextField(name = "id") 
    title = TextField(name = "title") 
    description = TextField(name = "description")
    vector = VectorField("vector", "FLAT", {
        "TYPE": "FLOAT32",
        "DIM": vec_dim,
        "DISTANCE_METRIC": "COSINE",
        "INITIAL_CAP": vec_len,
    })

    try:
        r_client.ft(VECTOR_INDEX).info()

        cfg.get_logger().info(f"index '{VECTOR_INDEX}' already exists")
    except:
        r_client.ft(VECTOR_INDEX).create_index(
            fields=[id, title, description, vector],
            definition=IndexDefinition(prefix=[DB_HASH_PREFIX], index_type=IndexType.HASH)
        )

        cfg.get_logger().info(f"created index '{VECTOR_INDEX}'")

    for key, value in data.items():
        doc_key = key_concat(DB_HASH_PREFIX, key)

        r_client.hset(doc_key, mapping={
            "id": value["id"],
            "title": value["title"],
            "description": value["description"],
            "vector": bytes(value["vector"])
        })
        cfg.get_logger().info(f"added document with key '{doc_key}'")