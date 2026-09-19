"""Interactive terminal interface."""

import sys

from config import report_error
from search import search_prompt


def chat_loop(ask, *, input_fn=input, output_fn=print) -> int:
    output_fn("Faça sua pergunta (sair para encerrar):")
    while True:
        try:
            question = input_fn("PERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("Até mais.")
            return 0
        if question.lower() in {"sair", "exit", "quit"}:
            return 0
        if not question:
            continue
        output_fn(f"RESPOSTA: {ask(question)}")
        output_fn("---")


def main() -> int:
    try:
        return chat_loop(search_prompt())
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        print(report_error("executar o chat", exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
