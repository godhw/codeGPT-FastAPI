import time
import threading
import logging

from fastapi import FastAPI, HTTPException

import config
import model

app = FastAPI()

logging.basicConfig(level=logging.INFO)
requests_queue = model.requests_queue

APIRequest = config.APIRequest
APIResponse = config.APIResponse

@app.on_event("startup")
async def startup_event():

    logging.info("start model thread")
    threading.Thread(target=model.handle_requests_by_batch).start()
    logging.info("thread start complete")

    logging.info("start server")

@app.post("/generate")
def generate(request: APIRequest)->APIResponse:
    if requests_queue.qsize() > model.BATCH_SIZE:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    req_data = request.dict()
    args = []
    
    code = req_data['code']
    max_length = int(req_data['max_length'])

    args.append(code)
    args.append(max_length)

    req = {'input': args}

    logging.info("input: ", req_data)
    requests_queue.put(req)

    while 'output' not in req:
        time.sleep(model.CHECK_INTERVAL)

    output = req['output']
    logging.info("output: ", output)

    if "error" in output:
        raise HTTPException(status_code=500, detail=f"Internal server error: {output['error']}")
    else:
        result = output["result"]
        return APIResponse(text=result)

@app.get("/healthz", status_code=200)
def check_health():
    return "healthy"
