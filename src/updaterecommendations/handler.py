import redis
import torch
from redis.commands.search.query import Query

from src.pyutils.nn import RecommendationModel
from src.pyutils.config import Config
from src.pyutils.keyconcat import key_concat
from src.pyutils.constants import BF_PREFIX, DB_HASH_PREFIX, LOCK_TIMEOUT, LOCK_PREFIX, MAX_RECOMMENDATIONS, SET_PREFIX, VECTOR_INDEX, MAX_RESULTS
from src.pyutils.model import Body


def handle(cfg: Config, r_client: redis.Redis, body: Body, model: RecommendationModel) -> None:
    k_lock = key_concat(LOCK_PREFIX, body["userId"])
    lock = r_client.lock(k_lock, LOCK_TIMEOUT)
    lock.acquire(blocking=True)

    cfg.get_logger().info(f"acquired lock {k_lock}")

    if body["positive"]:
        k_vec = key_concat(DB_HASH_PREFIX, body["itemId"])
        vec = r_client.hget(k_vec, "vector")

        base_query = f"*=>[KNN {MAX_RESULTS} @vector $vector AS vector_score]"

        cursor = 0
        condition = True
        count = 0

        while condition:
            query = (
                Query(base_query)
                .return_fields("iid", "vector", "vector_score")
                .sort_by("vector_score")
                .paging(cursor, cursor + MAX_RESULTS)
                .dialect(2)
            )
            params_dict = {"vector": vec}

            results = r_client.ft(VECTOR_INDEX).search(query, params_dict)
            
            for article in results.docs:
                cfg.get_logger().info(f"found result for key {k_vec}: {article}")

                k_bf = key_concat(BF_PREFIX, body["userId"])
                exists = r_client.bf().exists(k_bf, body["itemId"])
                if exists:
                    cfg.get_logger().info(f"skipping result as exists within filter {k_bf}")

                    continue

                score = article.vector_score
                if model.user_exists(body["userId"]):
                    score = model(body["userId"], torch.tensor(article.vector)).item()

                k_set = key_concat(SET_PREFIX, body["userId"])
                r_client.zadd(k_set, {article.iid: score})

                cfg.get_logger().info(f"adding result {body['itemId']} to set {k_set}")

            k_count = key_concat(SET_PREFIX, body["userId"])
            count = r_client.zcount(k_count, -1, 1)

            cfg.get_logger().info(f"count for {k_count} is {count}")

            condition = count < MAX_RECOMMENDATIONS and len(results.docs) == count
            cursor += MAX_RESULTS

        to_remove = count - MAX_RECOMMENDATIONS
        if to_remove > 0:
            k_remove = key_concat(SET_PREFIX, body["userId"])
            r_client.zpopmin(k_remove, to_remove)

            cfg.get_logger().info(f"removed for {k_remove} is {to_remove}")

    else:
        k_bf = key_concat(BF_PREFIX, body["userId"])
        r_client.bf().add(k_bf)

        cfg.get_logger().info(f"added key {k_bf} to filter")

        k_set = key_concat(SET_PREFIX, body["userId"])
        r_client.zrem(k_set, body["itemId"])

        cfg.get_logger().info(f"added item {body['itemId']} to {k_set}")

    lock.release()

    cfg.get_logger().info(f"released lock {k_lock}")