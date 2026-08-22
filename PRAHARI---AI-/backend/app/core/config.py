"""Application configuration."""
import os
from pathlib import Path

# Load a local .env file (KEY=VALUE lines) if present — zero dependency parser.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        # do not override a value already set in the real environment
        os.environ.setdefault(key, val)


_load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "app" / "data"
MODEL_DIR = BASE_DIR / ".models"
MODEL_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{BASE_DIR / 'prahari.db'}"

APP_NAME = "Prahari — Digital Public Safety Intelligence Platform"
APP_VERSION = "1.0.0"

# CORS origins for the Vite dev server + preview
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://localhost:3000",
    "*",
]

# Risk thresholds shared across modules
SCAM_ALERT_THRESHOLD = 0.60
SCAM_CRITICAL_THRESHOLD = 0.85

# ---- Google Gemini (Google AI Studio) --------------------------------------
# Get a free API key at https://aistudio.google.com/app/apikey and set it via
# the GEMINI_API_KEY environment variable or a backend/.env file. When unset,
# the platform runs fully on its built-in ML/rule engines (graceful fallback).
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
GEMINI_API_BASE = os.getenv(
    "GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta"
).strip()
