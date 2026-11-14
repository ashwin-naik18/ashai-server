import uuid
from redis_client import redis_client

STREAM_NAME = "ashai:inference:stream"


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