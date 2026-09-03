import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip().strip('"').strip("'")


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    log_level: str


def load_settings() -> Settings:
    settings = Settings(
        gemini_api_key=_env("GEMINI_API_KEY"),
        gemini_model=_env("GEMINI_MODEL", "gemini-2.0-flash"),
        log_level=_env("LOG_LEVEL", "INFO"),
    )
    if not settings.gemini_api_key:
        raise ValueError(
            "Falta GEMINI_API_KEY. Cópiala en .env (entre comillas) desde Google AI Studio."
        )
    return settings
