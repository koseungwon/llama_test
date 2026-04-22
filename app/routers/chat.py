from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_service import chat, clear_session

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, summary="RAG 기반 채팅")
async def chat_endpoint(request: ChatRequest):
    try:
        answer, sources, session_id = chat(request.message, request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM 호출 실패: {str(e)}")

    return ChatResponse(answer=answer, sources=sources, session_id=session_id)


@router.delete("/session/{session_id}", summary="대화 이력 초기화")
async def clear_chat_session(session_id: str):
    clear_session(session_id)
    return {"session_id": session_id, "message": "대화 이력이 초기화되었습니다."}
