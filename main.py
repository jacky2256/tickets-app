import logging
from pathlib import Path

from app.logutils import init_logger
from app.service import FileReaderService
from app.settings import LOG_DIR

init_logger(filename=str("{}.log".format(Path(__file__).stem)), logdir=str(LOG_DIR))


def main():
    try:
        FileReaderService().process_ser()
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    main()