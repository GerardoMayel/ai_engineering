from google import genai
from google.genai import types

from core.config import Settings
from core.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Cliente de Gemini con historial en memoria y generación parametrizable."""

    def __init__(self, settings: Settings) -> None:
        self.model = settings.gemini_model
        self._settings = settings
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
        return self._text_from(response)

    def complete(
        self,
        user_message: str,
        *,
        system_instruction: str,
        temperature: float | None = None,
    ) -> str:
        """Llamada sin historial: cada prompt de la cadena lleva su propio system."""
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=(
                self._settings.temperature if temperature is None else temperature
            ),
            top_p=self._settings.top_p,
            top_k=self._settings.top_k,
            max_output_tokens=self._settings.max_output_tokens,
        )
        logger.debug(
            "complete() modelo=%s temperature=%s (%s caracteres)",
            self.model,
            config.temperature,
            len(user_message),
        )
        response = self._client.models.generate_content(
            model=self.model,
            contents=user_message,
            config=config,
        )
        return self._text_from(response)

    @staticmethod
    def _text_from(response: object) -> str:
        text = (getattr(response, "text", None) or "").strip()
        if not text:
            logger.warning("El modelo devolvió una respuesta vacía")
            return "(sin respuesta)"
        return text
