# Validação rápida

Na raiz, Python 3.12: `python3.12 -m venv .venv`, ativar, instalar `requirements.txt` e `requirements-dev.txt`.
Copiar `.env.example` para `.env` e preencher apenas localmente OPENAI_API_KEY.
`docker compose up -d --wait`; `python src/ingest.py`; `python src/chat.py`.
Testes locais: `python -m pytest -q`. Banco real isolado: `RUN_DB_TESTS=1 python -m pytest tests/test_pgvector.py -q`.
Aceitação com LLM: após ingestão, `python scripts/evaluate_live.py`; revisar resposta coberta e três recusas. Não confundir integração determinística com qualidade real da LLM.
Detalhes operacionais no README. Não há comando automático de exclusão de volume.
