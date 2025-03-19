import logging
from pathlib import Path


def init_logger(filename=None, logdir=None):
    if not filename:
        filename = Path(__file__).stem
    else:
        filename = Path(filename).stem
    if not logdir:
        logdir = Path(__file__).parent
    else:
        logdir = Path(logdir).absolute()

    lp = "{}.log".format(str(logdir.joinpath(filename)))
    try:
        logging.basicConfig(filename=lp,
                            filemode='w',
                            force=True,
                            level=logging.INFO,
                            format='%(asctime)s %(filename)s [%(lineno)s] %(levelname)s: %(message)s')

        formatter = logging.Formatter('%(asctime)s %(filename)s [%(lineno)s] %(levelname)s: %(message)s')

        root_logger = logging.getLogger('')
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                root_logger.removeHandler(handler)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        root_logger.addHandler(console)

        logger = logging.getLogger(__name__)

        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    except Exception as err:
        raise SystemExit(err)

    return logger
