from datetime import datetime, timezone, timedelta
from redis.exceptions import RedisError
import logging
from fastapi import HTTPException

from redis_client import redis_client

DAILY_LIMIT = 100

logger = logging.getLogger("__name__")

def build_rate_limit_key(api_key_id : int):
    now = datetime.now(timezone.utc)
    
    a = now.strftime("%Y-%m-%d")   

    root = f"ashai:ratelimit:daily:{api_key_id}:{a}"
    
    reset_at = (
        now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ) + timedelta(days=1)
    )
    
    return root, reset_at.timestamp()

RATE_LIMIT_LUA = """
local current_count = tonumber(
    redis.call("GET", KEYS[1]) or "0"
)

local limit = tonumber(ARGV[1])

if current_count >= limit then
    return {0, current_count}
end

local new_count = redis.call("INCR", KEYS[1])

if new_count == 1 then
    redis.call("EXPIREAT", KEYS[1], ARGV[2])
end

return {1, new_count}
"""

rate_limit_script = redis_client.register_script(RATE_LIMIT_LUA)


def check_rate_limit(api_key_id : int):
    redis_key, reset_timestamp = build_rate_limit_key(api_key_id)
    
    try: 
    
        result = rate_limit_script(
            keys=[redis_key],
            args=[DAILY_LIMIT, int(reset_timestamp)]
        )
        
        allowed, request_count = result
        
        remaining_request = max(DAILY_LIMIT - request_count, 0)

        return {
            "allowed" : bool(allowed),
            "limit" : DAILY_LIMIT,
            "used" : request_count,
            "remaining" : remaining_request,
            "reset_at" : reset_timestamp
        }
        
    except RedisError:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily not available. Try again later."
        )
        
    except Exception as e:
        logger.exception("Unexpected Error in rate limiter")
    
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )