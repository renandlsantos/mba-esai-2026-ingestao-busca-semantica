"""Configuration and infrastructure factories; imports do not read user secrets."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    database_url: str = field(repr=False)
    collection: str
    embedding_model: str
    chat_model: str
    pdf_path: Path
    base_url: str | None = field(default=None, repr=False)
    timeout: float = 300
    max_tokens: int = 4096

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None):
        if env is None:
            # Explicit files only; blanks in templates must not mask external values.
            local = dotenv_values(ROOT / ".env", interpolate=False)
            resolved = {k: v for k, v in local.items() if v and v.strip()}
            resolved.update({k: v for k, v in os.environ.items() if v.strip()})
            if resolved.get("LLM_ENV_FILE"):
                credentials = Path(resolved["LLM_ENV_FILE"]).expanduser()
                if not credentials.is_file():
                    raise ValueError("LLM_ENV_FILE não encontrado.")
                external = dotenv_values(credentials, interpolate=False)
                for key, value in external.items():
                    if value and value.strip():
                        resolved.setdefault(key, value)
            env = resolved
        api_key = (env.get("SPARK_API_KEY") or env.get("OPENAI_API_KEY", "")).strip()
        if not api_key:
            raise ValueError("Configure OPENAI_API_KEY no ambiente ou no arquivo .env local.")
        database_url = (
            env.get("DATABASE_URL") or "postgresql+psycopg://postgres:postgres@localhost:55433/rag"
        )
        if not database_url.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL deve usar postgresql+psycopg://.")
        collection = (env.get("PG_VECTOR_COLLECTION_NAME") or "mba_esai_293_v1").strip()
        if not collection:
            raise ValueError("PG_VECTOR_COLLECTION_NAME não pode ser vazio.")
        pdf_path = Path(env.get("PDF_PATH") or "document.pdf").expanduser()
        if not pdf_path.is_absolute():
            pdf_path = ROOT / pdf_path
        base_url = (
            env.get("SPARK_BASE_URL")
            or env.get("OPENAI_BASE_URL")
            or env.get("OPENAI_API_BASE")
            or ""
        ).strip() or None
        if env.get("SPARK_API_KEY", "").strip() and not base_url:
            raise ValueError("SPARK_API_KEY exige base URL explícita; nenhum fallback remoto.")
        if base_url:
            parsed = urlsplit(base_url)
            if (
                parsed.scheme not in ("http", "https")
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("Base URL deve ser HTTP(S), sem credenciais ou query.")
        timeout = float(env.get("LLM_TIMEOUT_SECONDS") or "300")
        max_tokens = int(env.get("LLM_MAX_TOKENS") or "4096")
        if not 1 <= timeout <= 1500 or not 400 <= max_tokens <= 32768:
            raise ValueError("Timeout deve ser 1–1500s e max_tokens 400–32768.")
        return cls(
            api_key=api_key,
            database_url=database_url,
            collection=collection,
            embedding_model=env.get("OPENAI_EMBEDDING_MODEL") or "text-embedding-3-small",
            chat_model=env.get("OPENAI_CHAT_MODEL") or "gpt-4.1-mini",
            pdf_path=pdf_path,
            base_url=base_url,
            timeout=timeout,
            max_tokens=max_tokens,
        )


def create_store(settings: Settings):
    from langchain_openai import OpenAIEmbeddings
    from langchain_postgres import PGVector

    embeddings = OpenAIEmbeddings(
        api_key=settings.api_key,
        model=settings.embedding_model,
        base_url=settings.base_url,
        check_embedding_ctx_length=settings.base_url is None,
        request_timeout=settings.timeout,
        max_retries=2,
    )
    return PGVector(
        embeddings=embeddings,
        connection=settings.database_url,
        collection_name=settings.collection,
        use_jsonb=True,
    )


def create_model(settings: Settings):
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        api_key=settings.api_key,
        model=settings.chat_model,
        temperature=0,
        base_url=settings.base_url,
        timeout=settings.timeout,
        max_tokens=settings.max_tokens,
        max_retries=2,
    )


def report_error(operation: str, error: Exception) -> str:
    # Do not expose exception text: SDK/DB exceptions can contain URLs or credentials.
    return (
        f"Falha ao {operation} ({type(error).__name__}). "
        "Confira o PDF, a configuração local, o banco e o acesso ao provedor."
    )
