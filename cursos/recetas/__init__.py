"""Clase 4: recetas mexicanas con Pydantic anidado y un agente con tools.

Nivel de aprendizaje: intermedio (después del chat hello-world y las cadenas).
Complejidad: validación de esquemas, modelos compuestos, function calling e I/O a CSV.
"""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"
