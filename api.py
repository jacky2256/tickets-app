import logging
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks
from cache import get_keywords_from_redis, set_status_keywords, get_status_keywords
from logutils import init_logger
from schemas import EntryKeywords
from service import MainProcess
from settings import LOG_DIR

init_logger(filename=str("{}.log".format(Path(__file__).stem)), logdir=str(LOG_DIR))

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.post("/start", status_code=202)
async def start_service(entries: EntryKeywords, background_tasks: BackgroundTasks):
    try:
        logging.info(f"Received request: {entries}")
        vivid_status = get_status_keywords()
        if vivid_status == False:
            set_status_keywords(True)
            service = MainProcess()
            background_tasks.add_task(service.process_ser, entries)

            return {"status": "Processing started"}
        else:
            return {"status": "Processing already started"}
    except Exception as err:
        logging.error(f"Error starting vivid service: {err}")
        return {"status": "Failed to start processing"}

@app.get('/status')
async def get_status():
    try:
        vivid_status = get_status_keywords()
        return {'status': vivid_status}
    except Exception as err:
        logging.error(f"Error getting vivid status: {err}")

@app.get('/data')
async def get_vivid_data():
    try:
        data = get_keywords_from_redis()
        return {'data': data}
    except Exception as err:
        logging.error(f"Error stopping vivid service: {err}")