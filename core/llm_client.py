from google import genai
from google.genai import types

from core.config import Settings
from core.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Cliente de Gemini con historial en memoria y generación parametrizable."""

    def __init__(self, settings: Settings) -> None:
        self.model = settings.gemini_model
        self._client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(
                timeout=settings.request_timeout_seconds * 1000
            ),
        )
        self._chat = self._client.chats.create(
            model=settings.gemini_model,
            config=types.GenerateContentConfig(
                system_instruction=settings.system_prompt,
                temperature=settings.temperature,
                top_p=settings.top_p,
                top_k=settings.top_k,
                max_output_tokens=settings.max_output_tokens,
            ),
        )
        logger.info(
            "Sesión iniciada model=%s temperature=%s top_p=%s top_k=%s max_output_tokens=%s",
            settings.gemini_model,
            settings.temperature,
            settings.top_p,
            settings.top_k,
            settings.max_output_tokens,
        )

    def chat(self, user_message: str) -> str:
        logger.debug("Enviando mensaje al modelo (%s caracteres)", len(user_message))
        response = self._chat.send_message(user_message)
        text = (response.text or "").strip()
        if not text:
            logger.warning("El modelo devolvió una respuesta vacía")
            return "(sin respuesta)"
        return text
