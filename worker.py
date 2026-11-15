import os
import socket 
from langchain_ollama import ChatOllama

from redis_client import redis_client
from redis.exceptions import ResponseError

STREAM_NAME = "ashai:inference:stream"
GROUP_NAME =  "ashai-workers"

CONSUMER_NAME = socket.gethostname()

BLOCK_MS = 5000


def ensure_consumer_group():
    try:
        redis_client.xgroup_create(
            name=STREAM_NAME,
            groupname=GROUP_NAME,
            id="0",
            mkstream=True
        )
        
    except ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
        

def consume_one_job():
    message = redis_client.xreadgroup(
        groupname=GROUP_NAME,
        consumername=CONSUMER_NAME,
        streams={STREAM_NAME : ">"},
        count=1,
        block=BLOCK_MS
    )
    
    if not message:
        return None
    
    stream_id = message[0][1][0][0]
    job_data = message[0][1][0][1]
    job_id = job_data['job_id']
    
    request = job_data['message']
    
    print(job_id)
    print(request)
    
    return stream_id, job_data

def process_job(job_data):
    llm = ChatOllama(model=job_data["model"])
    
    message = job_data['message']
    
    response = llm.invoke(message)
    
    return response.content