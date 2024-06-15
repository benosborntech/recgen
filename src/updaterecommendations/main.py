import os
import openai
import redis
from ..pyutils.config import Config

openai_client = openai.OpenAI(
    api_key=os.environ["OPENAI_KEY"]
)

FILE = "data.json"
REDIS_ADDR = os.environ["REDIS_ADDR"]
KAFKA_BROKER = os.environ["KAFKA_BROKER"]

def main() -> None:
    cfg = Config()

    rdb = redis.Redis(
        host=REDIS_ADDR
    )

    pass

main()