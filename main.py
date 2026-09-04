import argparse

from chains.analisis_completo import analizar, format_reporte
from core.config import load_settings
from core.llm_client import LLMClient
from core.logger import get_logger

EXIT_COMMANDS = {"salir", "exit", "quit", "q"}


def _read_documento() -> str:
    print("Pega el texto a analizar. Línea vacía o Ctrl+D para enviar.\n")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _run_analisis(llm: LLMClient) -> None:
    texto = _read_documento()
    if not texto:
        print("No hay texto para analizar.")
        return
    logger = get_logger()
    try:
        resultado = analizar(texto, llm)
    except Exception:
        logger.exception("Error en la cadena de análisis")
        print("Hubo un error al ejecutar la cadena. Revisa logs y tu API key.")
        return
    print()
    print(format_reporte(resultado))


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat Gemini o cadena de análisis.")
    parser.add_argument(
        "--analisis",
        action="store_true",
        help="Ejecuta clasificador → resumidor → extractor sobre un texto.",
    )
    args = parser.parse_args()

    settings = load_settings()
    logger = get_logger(level=settings.log_level)
    llm = LLMClient(settings)

    if args.analisis:
        _run_analisis(llm)
        return

    print(f"Chat con Gemini ({settings.gemini_model})")
    print(
        "params: "
        f"temperature={settings.temperature} "
        f"top_p={settings.top_p} "
        f"top_k={settings.top_k} "
        f"max_output_tokens={settings.max_output_tokens}"
    )
    print("Escribe tu mensaje. Comandos: salir / exit / quit / Ctrl+C")
    print("Cadena de análisis: python main.py --analisis\n")

    while True:
        try:
            user_message = input("tú > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nHasta luego.")
            break

        if not user_message:
            continue
        if user_message.lower() in EXIT_COMMANDS:
            print("Hasta luego.")
            break

        try:
            reply = llm.chat(user_message)
        except Exception:
            logger.exception("Error al llamar a Gemini")
            print("asistente > Hubo un error al hablar con el modelo. Revisa logs y tu API key.")
            continue

        print(f"asistente > {reply}\n")


if __name__ == "__main__":
    main()
