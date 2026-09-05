from pydantic import BaseModel, Field, field_validator


class Ingrediente(BaseModel):
    nombre: str = Field(..., min_length=1)
    cantidad: float = Field(..., gt=0)
    unidad: str = Field(..., min_length=1)

    @field_validator("nombre", "unidad")
    @classmethod
    def _strip(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("no puede estar vacío")
        return cleaned


class Receta(BaseModel):
    titulo: str = Field(..., min_length=1)
    ingredientes: list[Ingrediente] = Field(..., min_length=1)
    pasos: list[str] = Field(..., min_length=1)

    @field_validator("titulo")
    @classmethod
    def _strip_titulo(cls, value: str) -> str:
        return value.strip()

    @field_validator("pasos")
    @classmethod
    def _pasos_no_vacios(cls, value: list[str]) -> list[str]:
        pasos = [paso.strip() for paso in value if paso.strip()]
        if not pasos:
            raise ValueError("debe haber al menos un paso")
        return pasos


class Recetario(BaseModel):
    recetas: list[Receta] = Field(..., min_length=10, max_length=10)


class RecetarioProsa(BaseModel):
    """Entrada cruda: título → instrucciones en texto libre."""

    recetas: dict[str, str] = Field(..., min_length=10, max_length=10)

    @field_validator("recetas")
    @classmethod
    def _textos_utiles(cls, value: dict[str, str]) -> dict[str, str]:
        cleaned: dict[str, str] = {}
        for titulo, texto in value.items():
            if not isinstance(texto, str):
                raise ValueError(f"la receta {titulo!r} debe ser un texto")
            nombre = titulo.strip()
            cuerpo = texto.strip()
            if not nombre or not cuerpo:
                raise ValueError(f"título o texto vacío: {titulo!r}")
            cleaned[nombre] = cuerpo
        if len(cleaned) != 10:
            raise ValueError("el archivo debe tener exactamente 10 recetas")
        return cleaned
