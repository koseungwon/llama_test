from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    session_id: str


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    file_type: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
    total: int


class DeleteResponse(BaseModel):
    doc_id: str
    message: str
