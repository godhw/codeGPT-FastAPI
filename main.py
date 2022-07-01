import time
import threading
import logging

from fastapi import FastAPI, HTTPException

import config
import model

app = FastAPI()

requests_queue = model.requests_queue
# logger setting
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

APIRequest = config.APIRequest
APIResponse = config.APIResponse

@app.on_event("startup")
async def startup_event():

    logger.info("start model thread")
    threading.Thread(target=model.handle_requests_by_batch).start()
    logger.info("thread start complete")

    logger.info("start server")

@app.post("/generate")
def generate(request: APIRequest)->APIResponse:
    # requests_queue is full?
    if requests_queue.qsize() > model.BATCH_SIZE:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    req_data = request.dict()
    args = []
    
    code = req_data['code']
    # type check
    max_length = int(req_data['max_length'])

    args.append(code)
    args.append(max_length)

    req = {'input': args}

    logger.info(f"input: {req_data}")

    # put the request to queue
    requests_queue.put(req)

    # wait for return
    while 'output' not in req:
        time.sleep(model.CHECK_INTERVAL)

    output = req['output']
    logger.info(f"output: {output}")

    # output check
    if "error" in output:
        raise HTTPException(status_code=500, detail=f"Internal server error: {output['error']}")
    else:
        result = output["result"]
        return APIResponse(text=result)

@app.get("/healthz", status_code=200)
def check_health():
    return "healthy"
