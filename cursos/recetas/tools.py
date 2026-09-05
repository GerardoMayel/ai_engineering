import csv
import json
from pathlib import Path

from google import genai
from google.genai import types

from core.config import load_settings
from cursos.recetas.jsonc import strip_jsonc
from cursos.recetas.models import Recetario, RecetarioProsa


def leer_archivo(ruta: str) -> str:
    """Lee un archivo de texto (JSONC/JSON) y devuelve su contenido."""
    path = Path(ruta).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    return path.read_text(encoding="utf-8")


def parsear_prosa(texto: str) -> RecetarioProsa:
    """Parsea JSONC del tipo {\"Guacamole\": \"Primero corta 1 cebolla...\"}."""
    payload = json.loads(strip_jsonc(texto))
    if not isinstance(payload, dict):
        raise ValueError("El JSONC debe ser un objeto {titulo: texto}.")
    if (
        set(payload) == {"recetas"}
        and isinstance(payload["recetas"], dict)
    ):
        payload = payload["recetas"]
    for clave, valor in payload.items():
        if isinstance(valor, dict):
            raise ValueError(
                "Las recetas deben ser prosa (un string), no objetos anidados. "
                f"Revisa {clave!r}."
            )
    return RecetarioProsa.model_validate({"recetas": payload})


def _estructurar_con_llm(prosa: RecetarioProsa) -> Recetario:
    settings = load_settings()
    client = genai.Client(api_key=settings.gemini_api_key)
    listado = "\n\n".join(
        f"## {titulo}\n{cuerpo}" for titulo, cuerpo in prosa.recetas.items()
    )
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=(
            "A partir de recetas en prosa, extrae un recetario estructurado. "
            "Usa los títulos dados. En cada receta lista ingredientes con "
            "nombre, cantidad numérica y unidad, y los pasos en orden. "
            "No inventes recetas extra: exactamente esas 10.\n\n"
            f"{listado}"
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
    """Lee recetas en prosa, las estructura con el LLM y valida el Recetario anidado."""
    prosa = parsear_prosa(texto)
    recetario = _estructurar_con_llm(prosa)
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
