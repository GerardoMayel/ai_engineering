from pathlib import Path

from google import genai
from google.genai import types

from core.config import load_settings
from cursos.recetas.tools import (
    exportar_csv_ingredientes,
    leer_archivo,
    validar_recetario,
)

SYSTEM = (
    "Eres un agente de recetas. Debes usar herramientas, no inventar datos si el archivo ya existe. "
    "Orden sugerido: leer_archivo → validar_recetario → exportar_csv_ingredientes. "
    "validar_recetario recibe el texto crudo y devuelve JSON. "
    "exportar_csv_ingredientes recibe ese JSON y la ruta de salida. "
    "Al terminar, confirma cuántas recetas y filas de ingredientes se escribieron."
)


def run_agent(ruta_entrada: str, ruta_salida: str) -> str:
    settings = load_settings()
    client = genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(
            timeout=settings.request_timeout_seconds * 1000
        ),
    )
    chat = client.chats.create(
        model=settings.gemini_model,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            temperature=0.1,
            tools=[leer_archivo, validar_recetario, exportar_csv_ingredientes],
        ),
    )
    entrada = str(Path(ruta_entrada).expanduser().resolve())
    salida = str(Path(ruta_salida).expanduser().resolve())
    prompt = (
        f"Lee el archivo {entrada}, valídalo como recetario de 10 recetas "
        f"y exporta el CSV de ingredientes a {salida}."
    )
    response = chat.send_message(prompt)
    return (response.text or "").strip()
