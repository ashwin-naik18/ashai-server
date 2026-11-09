from redis_client import redis_url, redis_client, check_redis
import redis

try:
    print("Redis Connection : ", check_redis())
    
    redis_client.set(
        "ashai:learning:project",
        "AshAI-Server",
        ex=60
    )
    
    value = redis_client.get("ashai:learning:project")
    
    print("Sorted Values : ", value)
    
    redis_client.incr("ashai:learning:counter")
    
    counter = redis_client.get("ashai:learning:counter")
    
    print("Counter: ", counter)
    
    redis_client.delete(
        "ashai:learning:project",
        "ashai:learning:counter"
    )
    
except redis.exceptions.RedisError as e:
    print(e)
    
finally:
    redis_client.close()