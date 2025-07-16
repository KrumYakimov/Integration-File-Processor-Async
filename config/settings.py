import os
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = os.path.join(BASE_DIR, "INPUT")

LOG_DIR = BASE_DIR / os.getenv("LOG_DIR", "logs")
LOG_TO_CONSOLE = config("LOG_TO_CONSOLE", default=False, cast=bool)

LOG_DIR.mkdir(parents=True, exist_ok=True)

PROCESS_TIME = config("PROCESS_TIME", default="18:10")
