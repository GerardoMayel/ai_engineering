from core.config import load_settings
from core.llm_client import LLMClient
from core.logger import get_logger

EXIT_COMMANDS = {"salir", "exit", "quit", "q"}


def main() -> None:
    settings = load_settings()
    logger = get_logger(level=settings.log_level)
    llm = LLMClient(settings)

    print(f"Chat con Gemini ({settings.gemini_model})")
    print(
        "params: "
        f"temperature={settings.temperature} "
        f"top_p={settings.top_p} "
        f"top_k={settings.top_k} "
        f"max_output_tokens={settings.max_output_tokens}"
    )
    print("Escribe tu mensaje. Comandos: salir / exit / quit / Ctrl+C\n")

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
