import logging
import torch

from transformers import AutoModelForCausalLM, AutoTokenizer
from queue import Queue, Empty

requests_queue = Queue()

# Queue size
BATCH_SIZE = 1

# Sleep interval
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
                    logging.info("transmit to model")
                    requests["output"] = make_code(requests['input'][0], requests['input'][1])

                except Exception as e:
                    requests["output"] = {'error': e}, 500

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
        return {'error': e}, 500
