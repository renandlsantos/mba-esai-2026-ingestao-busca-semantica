"""Configuration and infrastructure factories; imports do not read user secrets."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    database_url: str = field(repr=False)
    collection: str
    embedding_model: str
    chat_model: str
    pdf_path: Path

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None):
        if env is None:
            load_dotenv(ROOT / ".env", override=False)
            env = os.environ
        api_key = env.get("OPENAI_API_KEY", "").strip()
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
        return cls(
            api_key=api_key,
            database_url=database_url,
            collection=collection,
            embedding_model=env.get("OPENAI_EMBEDDING_MODEL") or "text-embedding-3-small",
            chat_model=env.get("OPENAI_CHAT_MODEL") or "gpt-4.1-mini",
            pdf_path=pdf_path,
        )


def create_store(settings: Settings):
    from langchain_openai import OpenAIEmbeddings
    from langchain_postgres import PGVector

    embeddings = OpenAIEmbeddings(
        api_key=settings.api_key,
        model=settings.embedding_model,
        request_timeout=60,
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
        timeout=60,
        max_retries=2,
    )


def report_error(operation: str, error: Exception) -> str:
    # Do not expose exception text: SDK/DB exceptions can contain URLs or credentials.
    return (
        f"Falha ao {operation} ({type(error).__name__}). "
        "Confira o PDF, a configuração local, o banco e o acesso ao provedor."
    )
