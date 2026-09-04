import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DEFAULT_SYSTEM_PROMPT = (
    "Eres un asistente de ingeniería de IA. Responde en español, "
    "de forma clara, precisa y útil."
)


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip().strip('"').strip("'")


def _env_float(name: str, default: float) -> float:
    raw = _env(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} debe ser un número, se recibió: {raw!r}") from exc


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} debe ser un entero, se recibió: {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    system_prompt: str
    temperature: float
    top_p: float
    top_k: int
    max_output_tokens: int
    request_timeout_seconds: int
    log_level: str

    def validate(self) -> None:
        if not self.gemini_api_key:
            raise ValueError(
                "Falta GEMINI_API_KEY. Cópiala en .env (entre comillas) desde Google AI Studio."
            )
        if not self.system_prompt:
            raise ValueError("SYSTEM_PROMPT no puede estar vacío.")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("TEMPERATURE debe estar entre 0.0 y 2.0.")
        if not 0.0 <= self.top_p <= 1.0:
            raise ValueError("TOP_P debe estar entre 0.0 y 1.0.")
        if self.top_k < 1:
            raise ValueError("TOP_K debe ser un entero >= 1.")
        if self.max_output_tokens < 1:
            raise ValueError("MAX_OUTPUT_TOKENS debe ser un entero >= 1.")
        if self.request_timeout_seconds < 1:
            raise ValueError("REQUEST_TIMEOUT_SECONDS debe ser un entero >= 1.")


def load_settings() -> Settings:
    settings = Settings(
        gemini_api_key=_env("GEMINI_API_KEY"),
        gemini_model=_env("GEMINI_MODEL", "gemini-3.6-flash"),
        system_prompt=_env("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT),
        temperature=_env_float("TEMPERATURE", 0.7),
        top_p=_env_float("TOP_P", 0.95),
        top_k=_env_int("TOP_K", 40),
        max_output_tokens=_env_int("MAX_OUTPUT_TOKENS", 1024),
        request_timeout_seconds=_env_int("REQUEST_TIMEOUT_SECONDS", 60),
        log_level=_env("LOG_LEVEL", "INFO"),
    )
    settings.validate()
    return settings
