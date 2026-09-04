from dataclasses import dataclass

from prompts.templates import clasificador, extractor, resumidor


@dataclass(frozen=True)
class PromptSpec:
    name: str
    system: str
    user: str
    temperature: float

    def render(self, **kwargs: str) -> str:
        return self.user.format(**kwargs)


def _from_module(module: object) -> PromptSpec:
    return PromptSpec(
        name=str(getattr(module, "NAME")),
        system=str(getattr(module, "SYSTEM")),
        user=str(getattr(module, "USER")),
        temperature=float(getattr(module, "TEMPERATURE")),
    )


REGISTRY: dict[str, PromptSpec] = {
    spec.name: spec
    for spec in (
        _from_module(clasificador),
        _from_module(resumidor),
        _from_module(extractor),
    )
}


def get_prompt(name: str) -> PromptSpec:
    try:
        return REGISTRY[name]
    except KeyError as exc:
        disponibles = ", ".join(sorted(REGISTRY))
        raise KeyError(f"Prompt desconocido: {name!r}. Disponibles: {disponibles}") from exc
