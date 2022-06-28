import torch
import io
import time
import threading
import random

from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict
from queue import Queue, Empty
from fastapi.staticfiles import StaticFiles
from transformers.utils.dummy_pt_objects import BLENDERBOT_PRETRAINED_MODEL_ARCHIVE_LIST

app = FastAPI()
#app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

requests_queue = Queue()
BATCH_SIZE = 2
CHECK_INTERVAL = 0.1

tokenizer = AutoTokenizer.from_pretrained("microsoft/CodeGPT-small-py")
model = AutoModelForCausalLM.from_pretrained("microsoft/CodeGPT-small-py")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def handle_requests_by_batch():
    while True:
        request_batch = []

        while not (len(request_batch) >= BATCH_SIZE):
            try:
                request_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue

            for requests in request_batch:
                try:
                    requests["output"] = make_code(requests['input'][0], requests['input'][1])

                except Exception as e:
                    requests["output"] = e

threading.Thread(target=handle_requests_by_batch).start()

def make_code(code, max_length):
    try:
        input_ids = tokenizer.encode(code, return_tensors='pt').to(device)

        max_length = max_length if max_length > 0 else 1

        gen_ids = model.generate(input_ids, max_length=max_length)

        result = dict()

        result["result"] = tokenizer.decode(gen_ids[0], skip_special_tokens=True)

        return result
    except Exception as e:
        print('Error occur in script gen', e)
        return jsonable_encoder({'error': e}), 500

@app.post("/generate")
async def generate(request: Request):
    if requests_queue.qsize() > BATCH_SIZE:
        raise HTTPException(status_code=429, detail="Too Many Requests")
    
    form_data = await request.form() 
    args = []
    code = form_data['code']
    max_length = int(form_data['max_length'])

    args.append(code)
    args.append(max_length)

    req = {'input': args}

    requests_queue.put(req)

    while 'output' not in req:
        time.sleep(CHECK_INTERVAL)

    output = req['output']

    if "error" in output:
        raise HTTPException(status_code=500, detail="Internal server error: {output['error']}")
    else:
        return jsonable_encoder(output)

@app.get("/healthz", status_code=200)
def check_health():
    return "healthy"
'''
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})
'''
