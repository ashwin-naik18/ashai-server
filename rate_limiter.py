from datetime import datetime, timezone, timedelta

from redis_client import redis_client

DAILY_LIMIT = 3


def build_rate_limit_key(api_key_id : int):
    now = datetime.now(timezone.utc)
    s = ""
    s += str(now.year)
    s += '-'
    s += str(now.month)
    s += '-'
    s += str(now.date)
    
    root = f"ashai:ratelimit:daily:{api_key_id}:{s}"
    
    reset_at = (
        now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ) + timedelta(days=1)
    )
    
    return root

print(build_rate_limit_key(1))