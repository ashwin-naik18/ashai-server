import uuid
from redis_client import redis_client

STREAM_NAME = "ashai:inference:stream"
from worker import GROUP_NAME

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