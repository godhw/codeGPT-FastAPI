import torch
import time
import threading
import logging

from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from queue import Queue, Empty

app = FastAPI()
logging.basicConfig(level=logging.INFO)
requests_queue = Queue()
BATCH_SIZE = 2
CHECK_INTERVAL = 0.1

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

tokenizer = AutoTokenizer.from_pretrained("microsoft/CodeGPT-small-py")
model = AutoModelForCausalLM.from_pretrained("microsoft/CodeGPT-small-py").to(device)



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
                    logging.info("correct")
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
        logging.error('Error occur in script gen', e)
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
