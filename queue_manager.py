import uuid
from redis_client import redis_client
import time


STREAM_NAME = "ashai:inference:stream"
GROUP_NAME =  "ashai-workers"

RESULT_TTL = 3600


def enqueue_job(message, model, user_id, api_key_id):
    job_id = str(uuid.uuid4())
    
    job_data = {
        "job_id" : str(job_id),
        "message" : message,
        "model" : model, 
        "user_id" : str(user_id),
        "api_key_id" : str(api_key_id)
    }
    
    redis_client.xadd(STREAM_NAME, job_data)
    
    return job_id


def store_result(job_id, response):
    key = f"ashai:inference:result:{job_id}"
    
    status = redis_client.set(key, response, ex=RESULT_TTL)
    
    return bool(status)


def acknowledge_job(stream_id):
    result = redis_client.xack(
        STREAM_NAME,
        GROUP_NAME,
        stream_id
    )
    
    return result   


def get_result(job_id):
    key = f"ashai:inference:result:{job_id}"
    
    return redis_client.get(key)


def wait_for_result(job_id, timeout = 30, poll_interval = 0.2):
    
    deadline = time.monotonic() + timeout
    
    while True:
        result = get_result(job_id)
        
        if result is not None:
            return result
        
        remaining_time = deadline - time.monotonic()
        
        if remaining_time <= 0:
            return None
        
        time.sleep(min(poll_interval, remaining_time))