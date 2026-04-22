from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat, documents

app = FastAPI(
    title="Llama 3.1 RAG API",
    description="다중 문서 기반 RAG 채팅 API (PDF, DOCX, XLSX, HWP 지원)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
