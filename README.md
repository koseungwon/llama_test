# Llama 3.1 RAG Chatbot API

Llama 3.1 8B + ChromaDB 기반 다중 문서 RAG 채팅 REST API

## 지원 파일 형식
- PDF (`.pdf`)
- Word (`.docx`, `.doc`)
- Excel (`.xlsx`, `.xls`)
- 한글 (`.hwp`)

## 설치 및 실행

### 1. Ollama 설치 및 모델 다운로드
```bash
# Ollama 설치 (https://ollama.com)
curl -fsSL https://ollama.com/install.sh | sh

# Llama 3.1 8B 모델 다운로드
ollama pull llama3.1:8b

# Ollama 서버 실행
ollama serve
```

### 2. Python 환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. API 서버 실행
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger UI: http://localhost:8000/docs

---

## API 사용법

### 문서 업로드
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@your_document.pdf"
```

### 채팅
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "문서에서 주요 내용을 알려줘"}'
```

응답:
```json
{
  "answer": "...",
  "sources": ["your_document.pdf"],
  "session_id": "uuid-..."
}
```

이어서 대화하려면 `session_id`를 포함:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "더 자세히 설명해줘", "session_id": "uuid-..."}'
```

### 문서 목록 조회
```bash
curl http://localhost:8000/documents
```

### 문서 삭제
```bash
curl -X DELETE http://localhost:8000/documents/{doc_id}
```

### 대화 이력 초기화
```bash
curl -X DELETE http://localhost:8000/chat/session/{session_id}
```

---

## 설정 변경 (.env)

```env
OLLAMA_MODEL=llama3.1:8b
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVER_K=5
```
