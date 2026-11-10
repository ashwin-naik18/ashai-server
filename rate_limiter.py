from datetime import datetime, timezone, timedelta

from redis_client import redis_client

DAILY_LIMIT = 3


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
    redis.call("GET", KEYS[1]), "0"
)

local limit = tonumber(ARGV[1])

if current >= limit then
    return {0, current_count}
end

local new_count = redis.call("INCR", KEYS[1])

if new_count == 1 then
    redis.call("EXPIREAT", ARGV[1], ARGV[2])
end

return {1, new_count}
"""

rate_limit_script = redis_client.register_script(RATE_LIMIT_LUA)