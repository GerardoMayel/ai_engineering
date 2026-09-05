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
    "Eres un agente de recetas. El archivo de entrada NO trae ingredientes estructurados: "
    "es un mapa titulo → texto libre (por ejemplo "
    '"Guacamole": "Primero corta 1 cebolla y 3 aguacates..."). '
    "Usa herramientas. Orden: leer_archivo → validar_recetario → exportar_csv_ingredientes. "
    "validar_recetario parsea la prosa, extrae ingredientes/pasos con el modelo y valida Pydantic. "
    "exportar_csv_ingredientes recibe el JSON estructurado y la ruta de salida. "
    "No inventes recetas que no estén en el archivo."
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
        f"Lee {entrada}. Son 10 recetas en prosa (titulo: texto). "
        f"Estrúcturalas y exporta el CSV de ingredientes a {salida}."
    )
    response = chat.send_message(prompt)
    return (response.text or "").strip()
