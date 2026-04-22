import uuid
from collections import defaultdict

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

from app.config import settings
from app.services.vector_store import similarity_search


# 세션별 대화 이력 (메모리 내 저장)
_chat_histories: dict[str, list[dict[str, str]]] = defaultdict(list)

_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["context", "history", "question"],
    template="""당신은 주어진 문서를 기반으로 질문에 답하는 한국어 전문 어시스턴트입니다.
반드시 아래 [참고 문서] 내용을 근거로 답변하세요.
문서에 없는 내용은 "제공된 문서에서 해당 정보를 찾을 수 없습니다."라고 답하세요.

[이전 대화]
{history}

[참고 문서]
{context}

[질문]
{question}

[답변]""",
)


def _get_llm() -> OllamaLLM:
    return OllamaLLM(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0.1,
    )


def chat(message: str, session_id: str | None = None) -> tuple[str, list[str], str]:
    if not session_id:
        session_id = str(uuid.uuid4())

    # 관련 문서 검색
    docs = similarity_search(message)
    context = "\n\n---\n\n".join(doc.page_content for doc in docs)
    sources = list({doc.metadata.get("filename", "") for doc in docs})

    # 이전 대화 이력 포맷
    history = _chat_histories[session_id]
    history_text = "\n".join(
        f"사용자: {h['user']}\n어시스턴트: {h['assistant']}" for h in history[-5:]
    ) if history else "없음"

    # LLM 호출
    prompt = _PROMPT_TEMPLATE.format(
        context=context,
        history=history_text,
        question=message,
    )
    llm = _get_llm()
    answer = llm.invoke(prompt)

    # 대화 이력 저장
    _chat_histories[session_id].append({"user": message, "assistant": answer})

    return answer, sources, session_id


def clear_session(session_id: str) -> None:
    _chat_histories.pop(session_id, None)
