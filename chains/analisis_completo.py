from __future__ import annotations

import json
import re
from typing import Any

from core.llm_client import LLMClient
from core.logger import get_logger
from prompts.registry import get_prompt

logger = get_logger(__name__)

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


def _parse_json(raw: str) -> Any:
    cleaned = _FENCE.sub("", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("No se pudo parsear JSON; se devuelve texto crudo")
        return {"raw": raw}


def _run(llm: LLMClient, name: str, **kwargs: str) -> str:
    spec = get_prompt(name)
    user_message = spec.render(**kwargs)
    logger.info("Paso de cadena: %s", name)
    return llm.complete(
        user_message,
        system_instruction=spec.system,
        temperature=spec.temperature,
    )


def analizar(texto: str, llm: LLMClient) -> dict[str, Any]:
    """Clasifica → resume → extrae. La extracción recibe la clasificación previa."""
    clasificacion_raw = _run(llm, "clasificador", texto=texto)
    clasificacion = _parse_json(clasificacion_raw)

    resumen = _run(llm, "resumidor", texto=texto)

    extraccion_raw = _run(
        llm,
        "extractor",
        texto=texto,
        clasificacion=json.dumps(clasificacion, ensure_ascii=False),
    )
    extraccion = _parse_json(extraccion_raw)

    return {
        "clasificacion": clasificacion,
        "resumen": resumen,
        "extraccion": extraccion,
    }


def format_reporte(resultado: dict[str, Any]) -> str:
    bloque = json.dumps(resultado, ensure_ascii=False, indent=2)
    return f"--- análisis completo ---\n{bloque}"
