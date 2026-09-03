from google import genai
from google.genai import types

from core.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Cliente mínimo de Gemini con historial de conversación en memoria."""

    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self._client = genai.Client(api_key=api_key)
        self._chat = self._client.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Eres un asistente útil. Responde de forma clara y concisa."
                )
            ),
        )
        logger.info("Sesión de chat iniciada con el modelo %s", model)

    def chat(self, user_message: str) -> str:
        logger.debug("Enviando mensaje al modelo (%s caracteres)", len(user_message))
        response = self._chat.send_message(user_message)
        text = (response.text or "").strip()
        if not text:
            logger.warning("El modelo devolvió una respuesta vacía")
            return "(sin respuesta)"
        return text
