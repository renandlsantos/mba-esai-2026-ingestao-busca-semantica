from pathlib import Path
from unittest.mock import Mock

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from config import Settings
from ingest import chunk_documents, ingest_pdf, load_pdf
from search import REFUSAL, answer_question
from chat import chat_loop


def test_settings_defaults_and_secret_not_in_repr():
    settings = Settings.from_env({"OPENAI_API_KEY": "test-secret"})
    assert settings.collection == "mba_esai_293_v1"
    assert "test-secret" not in repr(settings)


@pytest.mark.parametrize("env", [{}, {"OPENAI_API_KEY": "x", "DATABASE_URL": "sqlite://"}])
def test_settings_invalid(env):
    with pytest.raises(ValueError):
        Settings.from_env(env)


def test_chunk_size_overlap_and_ids():
    chunks = chunk_documents(
        [Document(page_content="x" * 2100, metadata={"page": 0})],
        "abc",
        "test",
        "test.pdf",
        "embed",
    )
    assert [len(d.page_content) for d in chunks] == [1000, 1000, 400]
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[0].metadata["document_sha256"] == "abc"


def test_missing_and_invalid_pdf(tmp_path):
    with pytest.raises(ValueError, match="PDF"):
        load_pdf(tmp_path / "missing.pdf")
    invalid = tmp_path / "bad.pdf"
    invalid.write_text("not a PDF")
    with pytest.raises(ValueError, match="PDF"):
        load_pdf(invalid)


def test_original_pdf_has_text():
    docs = load_pdf(Path(__file__).resolve().parents[1] / "document.pdf")
    assert docs and any(d.page_content.strip() for d in docs)


def test_ingestion_reuses_ids_and_keeps_collection_separate(monkeypatch):
    monkeypatch.setattr(
        "ingest.load_pdf", lambda p: [Document(page_content="some text", metadata={"page": 0})]
    )
    settings = Settings.from_env({"OPENAI_API_KEY": "test"})
    store = Mock()
    assert ingest_pdf(settings, store=store) == 1
    ids = store.add_documents.call_args.kwargs["ids"]
    ingest_pdf(settings, store=store)
    assert store.add_documents.call_args.kwargs["ids"] == ids
    assert len(ids) == len(set(ids)) == 1


def test_empty_document_rejected(monkeypatch):
    monkeypatch.setattr("ingest.load_pdf", lambda p: [Document(page_content=" ")])
    store = Mock()
    with pytest.raises(ValueError, match="texto"):
        ingest_pdf(Settings.from_env({"OPENAI_API_KEY": "test"}), store=store)
    store.add_documents.assert_not_called()


def test_retrieval_uses_ten_and_prompt_includes_evidence_and_rules():
    store = Mock()
    store.similarity_search_with_score.return_value = [
        (Document(page_content="Receita: 10 milhões."), 0.1)
    ]
    model = Mock()
    model.invoke.return_value = AIMessage(content="10 milhões.")
    assert answer_question("Qual a receita?", store, model) == "10 milhões."
    store.similarity_search_with_score.assert_called_once_with("Qual a receita?", k=10)
    messages = model.invoke.call_args.args[0]
    prompt = messages[-1].content
    assert "Receita: 10 milhões." in prompt
    assert "Qual a receita?" in prompt
    assert REFUSAL in prompt
    assert "Nunca invente ou use conhecimento externo." in prompt


def test_no_context_refuses_without_model():
    store, model = Mock(), Mock()
    store.similarity_search_with_score.return_value = []
    assert answer_question("Qual a capital?", store, model) == REFUSAL
    model.invoke.assert_not_called()


def test_blank_question_does_not_query():
    store, model = Mock(), Mock()
    with pytest.raises(ValueError):
        answer_question("  ", store, model)
    store.similarity_search_with_score.assert_not_called()


def test_empty_model_output_refuses():
    store, model = Mock(), Mock()
    store.similarity_search_with_score.return_value = [(Document(page_content="ABC"), 0.2)]
    model.invoke.return_value = AIMessage(content="  ")
    assert answer_question("Q", store, model) == REFUSAL


def test_cli_multiple_questions_and_blank_input():
    inputs = iter(["", "Q1", "Q2", "sair"])
    output = []
    ask = Mock(side_effect=["A1", "A2"])
    assert chat_loop(ask, input_fn=lambda _: next(inputs), output_fn=output.append) == 0
    assert ask.call_count == 2
    assert "RESPOSTA: A1" in output and "RESPOSTA: A2" in output


@pytest.mark.parametrize("error", [EOFError, KeyboardInterrupt])
def test_cli_clean_exit(error):
    def read(_):
        raise error

    assert chat_loop(Mock(), input_fn=read, output_fn=lambda _: None) == 0


def test_service_failure_is_not_a_success():
    store, model = Mock(), Mock()
    store.similarity_search_with_score.side_effect = RuntimeError("database offline")
    with pytest.raises(RuntimeError):
        answer_question("Q", store, model)


def test_chat_failure_returns_nonzero_without_secrets(monkeypatch, capsys):
    import chat

    monkeypatch.setattr(
        chat, "search_prompt", Mock(side_effect=RuntimeError("postgresql://secret-password"))
    )
    assert chat.main() == 1
    error = capsys.readouterr().err
    assert "RuntimeError" in error and "secret-password" not in error


def test_ingestion_failure_returns_nonzero(monkeypatch, capsys):
    import ingest

    monkeypatch.setattr(ingest, "ingest_pdf", Mock(side_effect=ValueError("private-path")))
    assert ingest.main() == 1
    output = capsys.readouterr()
    assert not output.out and "private-path" not in output.err


def test_search_failure_returns_nonzero(monkeypatch, capsys):
    import search

    monkeypatch.setattr("sys.argv", ["search.py", "Q"])
    monkeypatch.setattr(search, "search_prompt", Mock(side_effect=RuntimeError("api-key-secret")))
    assert search.main() == 1
    assert "api-key-secret" not in capsys.readouterr().err


def test_split_overlap_contains_same_characters():
    original = "".join(chr(0x400 + i) for i in range(2100))
    chunks = chunk_documents([Document(page_content=original)], "abc", "test", "x.pdf", "embed")
    assert chunks[0].page_content[-150:] == chunks[1].page_content[:150]
    assert chunks[1].page_content[-150:] == chunks[2].page_content[:150]


def test_spark_configuration_and_factories(monkeypatch):
    import langchain_openai
    import langchain_postgres
    from config import create_model, create_store

    settings = Settings.from_env(
        {
            "SPARK_API_KEY": "private-test",
            "SPARK_BASE_URL": "http://spark.test/v1",
            "OPENAI_CHAT_MODEL": "spark/code",
            "OPENAI_EMBEDDING_MODEL": "spark/embed",
        }
    )
    chat, embeddings, pgvector = Mock(), Mock(), Mock()
    monkeypatch.setattr(langchain_openai, "ChatOpenAI", chat)
    monkeypatch.setattr(langchain_openai, "OpenAIEmbeddings", embeddings)
    monkeypatch.setattr(langchain_postgres, "PGVector", pgvector)
    create_model(settings)
    create_store(settings)
    assert chat.call_args.kwargs["base_url"] == "http://spark.test/v1"
    assert chat.call_args.kwargs["timeout"] == 300
    assert chat.call_args.kwargs["max_tokens"] == 4096
    # Compatible servers accept text, not OpenAI tokenizer integer arrays.
    assert embeddings.call_args.kwargs["check_embedding_ctx_length"] is False
    assert embeddings.call_args.kwargs["base_url"] == "http://spark.test/v1"
    assert "private-test" not in repr(settings)


@pytest.mark.parametrize(
    "extra",
    [
        {"OPENAI_BASE_URL": "http://user:secret@spark.test/v1"},
        {"OPENAI_BASE_URL": "file:///tmp/api"},
        {"LLM_TIMEOUT_SECONDS": "nan"},
        {"LLM_MAX_TOKENS": "50"},
    ],
)
def test_reject_unsafe_or_unusable_provider_settings(extra):
    with pytest.raises(ValueError):
        Settings.from_env({"OPENAI_API_KEY": "test", **extra})


def test_external_credentials_file_is_explicit_and_not_copied(tmp_path, monkeypatch):
    import config

    external = tmp_path / "credentials.env"
    external.write_text("SPARK_API_KEY=test-external-key\nSPARK_BASE_URL=http://spark.test/v1\n")
    monkeypatch.setattr(config, "ROOT", tmp_path)
    for name in ("SPARK_API_KEY", "SPARK_BASE_URL", "OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_API_BASE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LLM_ENV_FILE", str(external))
    settings = Settings.from_env()
    assert settings.api_key == "test-external-key"
    assert settings.base_url == "http://spark.test/v1"
    assert not (tmp_path / ".env").exists()
    assert "SPARK_API_KEY" not in config.os.environ
    assert "SPARK_BASE_URL" not in config.os.environ


def test_spark_key_without_endpoint_cannot_fall_back_to_openai():
    with pytest.raises(ValueError, match="base URL explícita"):
        Settings.from_env({"SPARK_API_KEY": "synthetic-spark-key"})


def test_blank_local_key_does_not_mask_external_openai_alias(tmp_path, monkeypatch):
    import config
    from unittest.mock import patch

    external = tmp_path / "external.env"
    external.write_text("OPENAI_API_KEY=synthetic-external\nOPENAI_BASE_URL=http://spark.test/v1\n")
    (tmp_path / ".env").write_text(f"OPENAI_API_KEY=\nLLM_ENV_FILE={external}\n")
    monkeypatch.setattr(config, "ROOT", tmp_path)
    with patch.dict(config.os.environ, {}, clear=True):
        settings = Settings.from_env()
        assert settings.api_key == "synthetic-external"
        assert settings.base_url == "http://spark.test/v1"
        assert "OPENAI_API_KEY" not in config.os.environ
