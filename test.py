# from concurrent.futures import ThreadPoolExecutor

# from rate_limiter import check_rate_limit, build_rate_limit_key
# from redis_client import redis_client

# api_key_id = 999002
# total_requests = 20

# key, _ = build_rate_limit_key(api_key_id)

# redis_client.delete(key)

# from concurrent.futures import ThreadPoolExecutor

# with ThreadPoolExecutor(max_workers=10) as executor:
#     results = list(executor.map(check_rate_limit, [api_key_id] * total_requests))
    
# allowed = sum(1 for r in results if r['allowed'])
# rejected = sum(1 for r in results if not r['allowed'])

# print(allowed)
# print(rejected)

# result = check_rate_limit(api_key_id)

# print(result)


# a = [
#     (
#         "ashai:inference:stream",
#         [
#             (
#                 "1794653287833-0",
#                 {
#                     "job_id": "c41da72b-a591-479b-b1f5-494e55699450",
#                     "message": "Explain Redis Streams",
#                     "model": "qwen3:1.7b",
#                     "user_id": "1",
#                     "api_key_id": "1"
#                 }
#             )
#         ]
#     )
# ]

# print(a[0][1][0][1])

from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen3:1.7b")

print(llm.invoke("hi").content)