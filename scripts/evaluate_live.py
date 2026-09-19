"""Opt-in acceptance run against the configured real provider. May incur API cost."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import Settings, create_model, create_store, report_error  # noqa: E402
from search import REFUSAL, answer_question  # noqa: E402

CASES = [
    ("Qual o faturamento da Empresa SuperTechIABrazil?", "covered"),
    ("Qual é a capital da França?", "absent"),
    ("Quantos clientes temos em 2024?", "absent"),
    ("Você acha isso bom ou ruim?", "absent"),
]


def main():
    try:
        settings = Settings.from_env()
        store, model = create_store(settings), create_model(settings)
        results = []
        for question, kind in CASES:
            answer = answer_question(question, store, model)
            correct = (
                answer == REFUSAL
                if kind == "absent"
                else (
                    "10.000.000" in answer
                    or "10 milhões" in answer
                    or "dez milhões" in answer.lower()
                )
            )
            results.append(
                {"question": question, "kind": kind, "answer": answer, "automatic_check": correct}
            )
        print(
            json.dumps(
                {
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                    "provider": "OpenAI",
                    "chat_model": settings.chat_model,
                    "embedding_model": settings.embedding_model,
                    "document_sha256": __import__("hashlib")
                    .sha256(settings.pdf_path.read_bytes())
                    .hexdigest(),
                    "results": results,
                    "human_review_required": True,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if all(item["automatic_check"] for item in results) else 1
    except Exception as exc:
        print(report_error("avaliar com modelo real", exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
