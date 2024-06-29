import redis
from redis.commands.search.query import Query

from src.pyutils.config import Config
from src.pyutils.keyconcat import key_concat
from src.pyutils.constants import BF_PREFIX, DB_HASH_PREFIX, LOCK_TIMEOUT, LOCK_PREFIX, MAX_RECOMMENDATIONS, SET_PREFIX, VECTOR_INDEX, MAX_RESULTS, PAGE_SIZE
from src.pyutils.model import Body


def handle(_: Config, r_client: redis.Redis, body: Body) -> None:
    lock = r_client.lock(key_concat(LOCK_PREFIX, body["userId"]), LOCK_TIMEOUT)
    lock.acquire(blocking=True)

    if body["positive"]:
        vec = r_client.hget(key_concat(DB_HASH_PREFIX, body["itemId"]), "vector")

        base_query = f"*=>[KNN {MAX_RESULTS} @vector $vector AS vector_score]"

        cursor = 0
        condition = True
        count = 0

        while condition:
            query = (
                Query(base_query)
                .return_fields("id", "vector", "vector_score")
                .sort_by("vector_score")
                .paging(cursor, cursor + MAX_RESULTS)
                .dialect(2)
            )
            params_dict = {"vector": vec}

            results = r_client.ft(VECTOR_INDEX).search(query, params_dict)
            
            for article in results.docs:
                exists = r_client.bf().exists(key_concat(BF_PREFIX, body["userId"]), body["itemId"])
                if exists:
                    continue

                r_client.zadd(key_concat(SET_PREFIX, body["userId"]), {body["itemId"]: article.vector_score})

            count = r_client.zcount(key_concat(SET_PREFIX, body["userId"]), 0, 1)

            condition = count < MAX_RECOMMENDATIONS and len(results) == count
            cursor += PAGE_SIZE

        to_remove = count - MAX_RECOMMENDATIONS
        if to_remove > 0:
            r_client.zpopmin(key_concat(SET_PREFIX, body["userId"]), to_remove)

    else:
        r_client.bf().add(key_concat(BF_PREFIX, body["userId"]))
        r_client.zrem(key_concat(SET_PREFIX, body["userId"]), body["itemId"])

    lock.release()