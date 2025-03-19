from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
LOG_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "app/config"
IN_DIR = BASE_DIR / "data/in"
OUT_DIR = BASE_DIR / "data/out"

VIVID_THREADS = 1
