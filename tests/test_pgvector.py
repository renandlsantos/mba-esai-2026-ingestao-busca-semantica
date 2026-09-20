"""Real PostgreSQL integration with deterministic TEST embeddings, never a real LLM."""

import hashlib
import os
import uuid

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector
from sqlalchemy import create_engine, text

from config import Settings
from ingest import ingest_pdf

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1", reason="Set RUN_DB_TESTS=1 for isolated DB"
    ),
]


class TestOnlyEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [self.embed_query(value) for value in texts]

    def embed_query(self, value):
        return [(b + 1) / 256 for b in hashlib.sha256(value.encode()).digest()[:8]]


def test_real_pgvector_persistence_upsert_retrieval_and_pdf():
    url = os.getenv(
        "TEST_DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:55433/rag"
    )
    collection = "test_293_" + uuid.uuid4().hex
    embeddings = TestOnlyEmbeddings()
    store = PGVector(
        embeddings=embeddings, connection=url, collection_name=collection, use_jsonb=True
    )
    engine = create_engine(url)
    try:
        docs = [Document(page_content=f"Documento de teste número {i}") for i in range(12)]
        ids = [collection + str(i) for i in range(12)]
        store.add_documents(docs, ids=ids)
        store.add_documents(docs, ids=ids)
        with engine.connect() as connection:
            count = connection.execute(
                text("""
                SELECT count(*) FROM langchain_pg_embedding e
                JOIN langchain_pg_collection c ON e.collection_id = c.uuid
                WHERE c.name = :name
            """),
                {"name": collection},
            ).scalar_one()
        assert count == 12
        reloaded = PGVector(
            embeddings=embeddings, connection=url, collection_name=collection, use_jsonb=True
        )
        results = reloaded.similarity_search_with_score(docs[3].page_content, k=10)
        assert len(results) == 10
        assert results[0][0].page_content == docs[3].page_content
        assert results[0][1] == pytest.approx(0.0, abs=1e-6)
        settings = Settings.from_env(
            {"OPENAI_API_KEY": "test-only", "PG_VECTOR_COLLECTION_NAME": collection}
        )
        amount = ingest_pdf(settings, store=store)
        assert amount > 0
        ingest_pdf(settings, store=store)
        with engine.connect() as connection:
            count = connection.execute(
                text("""
                SELECT count(*) FROM langchain_pg_embedding e
                JOIN langchain_pg_collection c ON e.collection_id = c.uuid
                WHERE c.name = :name
            """),
                {"name": collection},
            ).scalar_one()
        assert count == 12 + amount
        reloaded._engine.dispose()
    finally:
        store.delete_collection()  # Only the UUID collection created by this test.
        store._engine.dispose()
        engine.dispose()
