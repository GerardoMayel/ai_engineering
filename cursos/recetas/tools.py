import csv
import json
from pathlib import Path

from google import genai
from google.genai import types
from pydantic import ValidationError

from core.config import load_settings
from cursos.recetas.jsonc import strip_jsonc
from cursos.recetas.models import Recetario


def leer_archivo(ruta: str) -> str:
    """Lee un archivo de texto (JSONC/JSON) y devuelve su contenido."""
    path = Path(ruta).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    return path.read_text(encoding="utf-8")


def _cargar_payload(texto: str) -> dict:
    cleaned = strip_jsonc(texto)
    payload = json.loads(cleaned)
    if isinstance(payload, list):
        return {"recetas": payload}
    if isinstance(payload, dict):
        return payload
    raise ValueError("El JSONC debe ser un objeto o una lista de recetas.")


def _normalizar_con_llm(texto: str) -> Recetario:
    settings = load_settings()
    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=(
            "Normaliza el siguiente texto a un recetario con exactamente 10 recetas. "
            "Conserva titulo, ingredientes (nombre, cantidad numérica, unidad) y pasos. "
            "Responde solo con el JSON del esquema.\n\n"
            f"{texto}"
        ),
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=Recetario,
        ),
    )
    raw = (response.text or "").strip()
    return Recetario.model_validate_json(raw)


def validar_recetario(texto: str) -> str:
    """Valida recetas con Pydantic (Ingrediente dentro de Receta). Si el JSONC falla, usa structured output."""
    try:
        recetario = Recetario.model_validate(_cargar_payload(texto))
    except (json.JSONDecodeError, ValidationError, ValueError, TypeError):
        recetario = _normalizar_con_llm(texto)
        recetario = Recetario.model_validate(recetario.model_dump())
    return recetario.model_dump_json(indent=2)


def exportar_csv_ingredientes(recetario_json: str, ruta_salida: str) -> str:
    """Escribe un CSV con una fila por ingrediente: titulo, nombre, cantidad, unidad."""
    recetario = Recetario.model_validate_json(recetario_json)
    path = Path(ruta_salida).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["titulo", "ingrediente", "cantidad", "unidad"])
        for receta in recetario.recetas:
            for item in receta.ingredientes:
                writer.writerow(
                    [receta.titulo, item.nombre, item.cantidad, item.unidad]
                )
    filas = sum(len(receta.ingredientes) for receta in recetario.recetas)
    return (
        f"CSV escrito en {path} con {len(recetario.recetas)} recetas "
        f"y {filas} filas de ingredientes."
    )
