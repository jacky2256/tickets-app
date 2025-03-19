from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
LOG_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "app/config"
IN_DIR = BASE_DIR / "data/in"
OUT_DIR = BASE_DIR / "data/out"
INPUT_CSV_FILE_PATH = BASE_DIR / "data/in/base.csv"
OUTPUT_CSV_FILE_PATH = BASE_DIR / "data/out/output.csv"
PROXIES_FILE_PATH = BASE_DIR / "data/in/proxies.txt"

USE_PROXY = False
MAX_FAILURES_PER_ONE_PROXY = 5
THREADS = 2
