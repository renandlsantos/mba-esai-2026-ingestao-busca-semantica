"""Read a textual PDF and upsert its chunks into pgVector."""

import hashlib
import sys
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import Settings, create_store, report_error

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def load_pdf(path: Path) -> list[Document]:
    if not path.is_file() or path.suffix.lower() != ".pdf":
        raise ValueError("PDF local não encontrado ou extensão inválida.")
    try:
        if not path.read_bytes().startswith(b"%PDF-"):
            raise ValueError("Assinatura PDF inválida.")
        pages = PyPDFLoader(str(path)).load()
    except Exception as exc:
        raise ValueError("PDF inválido, criptografado ou ilegível.") from exc
    if not any(page.page_content.strip() for page in pages):
        raise ValueError("PDF sem texto extraível; OCR não faz parte deste projeto.")
    return pages


def chunk_documents(pages, document_hash, collection, filename, embedding_model):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    split = splitter.split_documents(pages)
    result = []
    for index, document in enumerate(split):
        if not document.page_content.strip():
            continue
        result.append(
            Document(
                page_content=document.page_content,
                metadata={
                    "source": filename,
                    "page": int(document.metadata.get("page", 0)),
                    "chunk_index": index,
                    "document_sha256": document_hash,
                    "embedding_model": embedding_model,
                    "collection": collection,
                },
            )
        )
    return result


def ingest_pdf(settings: Settings | None = None, *, store=None) -> int:
    settings = settings or Settings.from_env()
    pages = load_pdf(settings.pdf_path)
    document_hash = hashlib.sha256(settings.pdf_path.read_bytes()).hexdigest()
    chunks = chunk_documents(
        pages,
        document_hash,
        settings.collection,
        settings.pdf_path.name,
        settings.embedding_model,
    )
    if not chunks:
        raise ValueError("PDF sem texto para indexar.")
    ids = [
        hashlib.sha256(
            f"{settings.collection}:{document_hash}:{d.metadata['chunk_index']}".encode()
        ).hexdigest()
        for d in chunks
    ]
    store = store if store is not None else create_store(settings)
    store.add_documents(documents=chunks, ids=ids)
    return len(chunks)


def main() -> int:
    try:
        count = ingest_pdf()
    except Exception as exc:
        print(report_error("ingerir o PDF", exc), file=sys.stderr)
        return 1
    print(f"Ingestão concluída: {count} trechos persistidos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
