import uuid
from pathlib import Path
from typing import Any

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from app.config import settings


_embeddings: HuggingFaceEmbeddings | None = None
_vector_store: Chroma | None = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is None:
        Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
        _vector_store = Chroma(
            collection_name="rag_documents",
            embedding_function=_get_embeddings(),
            persist_directory=settings.chroma_persist_dir,
        )
    return _vector_store


def add_document(text: str, filename: str, file_type: str) -> tuple[str, int]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)

    doc_id = str(uuid.uuid4())
    documents = [
        Document(
            page_content=chunk,
            metadata={"doc_id": doc_id, "filename": filename, "file_type": file_type, "chunk_index": i},
        )
        for i, chunk in enumerate(chunks)
    ]

    store = get_vector_store()
    store.add_documents(documents)
    return doc_id, len(chunks)


def similarity_search(query: str, k: int | None = None) -> list[Document]:
    store = get_vector_store()
    return store.similarity_search(query, k=k or settings.retriever_k)


def delete_document(doc_id: str) -> None:
    store = get_vector_store()
    results = store.get(where={"doc_id": doc_id})
    ids = results.get("ids", [])
    if ids:
        store.delete(ids=ids)


def list_documents() -> list[dict[str, Any]]:
    store = get_vector_store()
    results = store.get()
    metadatas = results.get("metadatas", [])

    seen: dict[str, dict[str, Any]] = {}
    for meta in metadatas:
        doc_id = meta.get("doc_id")
        if doc_id not in seen:
            seen[doc_id] = {
                "doc_id": doc_id,
                "filename": meta.get("filename", ""),
                "file_type": meta.get("file_type", ""),
                "chunk_count": 0,
            }
        seen[doc_id]["chunk_count"] += 1

    return list(seen.values())
