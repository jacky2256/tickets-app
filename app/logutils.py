import logging
from pathlib import Path

class IgnoreUnwantedMessagesFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()

        if "connectionpool" in msg or "start error" in msg or "X11 display failed" in msg:
            return False
        return True

def init_logger(filename=None, logdir=None):
    if not filename:
        filename = Path(__file__).stem
    else:
        filename = Path(filename).stem
    if not logdir:
        logdir = Path(__file__).parent
    else:
        logdir = Path(logdir).absolute()

    log_path = f"{str(logdir.joinpath(filename))}.log"
    try:
        logging.basicConfig(
            filename=log_path,
            filemode='w',
            force=True,
            level=logging.INFO,
            format='%(asctime)s %(filename)s [%(lineno)s] %(levelname)s: %(message)s'
        )

        formatter = logging.Formatter('%(asctime)s %(filename)s [%(lineno)d] %(levelname)s: %(message)s')

        root_logger = logging.getLogger('')

        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                root_logger.removeHandler(handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        console_handler.addFilter(IgnoreUnwantedMessagesFilter())
        root_logger.addHandler(console_handler)

        logger = logging.getLogger(__name__)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

    except Exception as err:
        raise SystemExit(err)

    return logger
