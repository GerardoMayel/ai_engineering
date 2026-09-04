import argparse
from pathlib import Path

from cursos.recetas import DATA_DIR
from cursos.recetas.agent import run_agent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agente Clase 4: JSONC de recetas → CSV de ingredientes."
    )
    parser.add_argument(
        "--entrada",
        default=str(DATA_DIR / "recetas_mexicanas.jsonc"),
        help="Ruta al JSONC de recetas.",
    )
    parser.add_argument(
        "--salida",
        default=str(DATA_DIR / "ingredientes.csv"),
        help="Ruta del CSV de ingredientes.",
    )
    args = parser.parse_args()

    Path(args.salida).parent.mkdir(parents=True, exist_ok=True)
    print(run_agent(args.entrada, args.salida))


if __name__ == "__main__":
    main()
