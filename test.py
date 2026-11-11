from concurrent.futures import ThreadPoolExecutor

from rate_limiter import check_rate_limit, build_rate_limit_key
from redis_client import redis_client

api_key_id = 999002
total_requests = 20

# key, _ = build_rate_limit_key(api_key_id)

# redis_client.delete(key)

from concurrent.futures import ThreadPoolExecutor

# with ThreadPoolExecutor(max_workers=10) as executor:
#     results = list(executor.map(check_rate_limit, [api_key_id] * total_requests))
    
# allowed = sum(1 for r in results if r['allowed'])
# rejected = sum(1 for r in results if not r['allowed'])

# print(allowed)
# print(rejected)

result = check_rate_limit(api_key_id)

print(result)