import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID")
GEE_SERVICE_ACCOUNT_JSON = os.getenv("GEE_SERVICE_ACCOUNT_JSON")
GEE_SERVICE_ACCOUNT_JSON_CONTENT = os.getenv("GEE_SERVICE_ACCOUNT_JSON_CONTENT")
TABPFN_TOKEN = os.getenv("TABPFN_TOKEN")

with open(DATA_DIR / "model_config.json") as f:
    MODEL_CONFIG = json.load(f)

FITUR_FINAL = MODEL_CONFIG["fitur_final"]
KOLOM_KABUPATEN = MODEL_CONFIG["kolom_kabupaten"]
KABUPATEN_LIST = MODEL_CONFIG["kabupaten_list"]
FITUR_INDEX = MODEL_CONFIG["fitur_index"]
KOLOM_LAG = MODEL_CONFIG["kolom_lag"]
KOLOM_DELTA = MODEL_CONFIG["kolom_delta"]
KOLOM_ROLL = MODEL_CONFIG["kolom_roll"]
KOLOM_TREND = MODEL_CONFIG["kolom_trend"]
TABPFN_BEST_PARAMS = MODEL_CONFIG["best_params"]