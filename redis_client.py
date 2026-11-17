import os
import redis

redis_url = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

redis_client = redis.Redis.from_url(
    redis_url,
    decode_responses = True,
    socket_connect_timeout = 2,
    socket_timeout = 10 ,
    health_check_interval = 30
)

def check_redis():
    return redis_client.ping()

