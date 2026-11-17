import os
import socket 
from langchain_ollama import ChatOllama
import uuid

from redis_client import redis_client
from redis.exceptions import ResponseError

from queue_manager import store_result, acknowledge_job 

import logging

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
STREAM_NAME = "ashai:inference:stream"
GROUP_NAME =  "ashai-workers"

CONSUMER_NAME = f"{socket.gethostname()}-{uuid.uuid4().hex[:8]}"

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
    llm = ChatOllama(
        model=job_data["model"],
        base_url=os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434"
        )
    )

    message = job_data["message"]

    response = llm.invoke(message)

    return response.content


def process_one_request():
    
    ensure_consumer_group()
    
    job = consume_one_job()
    
    if job is None:
        return False
    
    stream_id, job_data = job
    
    response = process_job(job_data)
    job_id = job_data['job_id']
    
    try:
    
        
        status = store_result(job_id, response)
        
        if not status:
            raise RuntimeError(
                f"Failed to store result for job_id = {job_id}"
            )
        
        acknowledgement_status = acknowledge_job(stream_id)

        if not acknowledgement_status:
            raise RuntimeError(
                f"Failed to acknowledge job_id = {job_id}"
            )
            
        logger.info(
            "Successfully processed job_id = %s",
            job_id  
        )
        
        return True
    
    except Exception :
        logger.exception(
            "Failed processing job_id = %s",
            job_id
        )
        
        raise   
    

def worker_loop():
    logger.info("Worker %s started", CONSUMER_NAME)
    
    try:
        while True:
            try:
                process_one_request()
                
            except KeyboardInterrupt:
                logger.info("Worker %s stopping...", CONSUMER_NAME)
                break
            
            except Exception:
                logger.exception(
                    "Worker %s encountered an error",
                    CONSUMER_NAME
                )
                
                
    finally:
        logger.info("Worker %s stopped..", CONSUMER_NAME) 
        
        
if __name__ == "__main__":
    worker_loop()           
    