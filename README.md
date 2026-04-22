# Llama 3.1 RAG Chatbot

Llama 3.1 8B + ChromaDB 기반 다중 문서 RAG 채팅 시스템  
REST API 및 웹 UI를 모두 제공합니다.

---

## 목차
1. [시스템 개요](#시스템-개요)
2. [기술 스택](#기술-스택)
3. [프로젝트 구조](#프로젝트-구조)
4. [지원 파일 형식](#지원-파일-형식)
5. [설치 및 실행](#설치-및-실행)
6. [웹 UI 사용법](#웹-ui-사용법)
7. [REST API 사용법](#rest-api-사용법)
8. [설정 변경](#설정-변경)
9. [동작 방식](#동작-방식)

---

## 시스템 개요

업로드한 문서(PDF, Word, Excel, HWP)를 벡터 DB에 저장하고,  
사용자가 채팅으로 질문하면 관련 문서를 검색해 Llama 3.1이 한국어로 답변합니다.

```
문서 업로드 → 텍스트 추출 → 청크 분할 → 임베딩 → ChromaDB 저장
질문 입력  → 유사 청크 검색 → 프롬프트 조립 → Llama 3.1 → 답변 + 출처
```

---

## 기술 스택

| 항목 | 기술 | 설명 |
|------|------|------|
| LLM | Llama 3.1 8B (Ollama) | 로컬 실행, Q4 양자화 (VRAM 4~5GB) |
| RAG 프레임워크 | LangChain | 문서 처리 및 RAG 파이프라인 |
| 벡터 DB | ChromaDB | 로컬 파일 기반, 별도 서버 불필요 |
| 임베딩 | jhgan/ko-sroberta-multitask | 한국어 특화 임베딩 모델 |
| API 서버 | FastAPI | REST API + 정적 파일 서빙 |
| 웹 UI | HTML + CSS + Vanilla JS | 별도 프레임워크 없이 FastAPI에서 직접 서빙 |

---

## 프로젝트 구조

```
llama_test/
├── app/
│   ├── main.py                 # FastAPI 앱 진입점, 웹 UI 서빙
│   ├── config.py               # 환경 설정 (모델명, 청크 크기 등)
│   ├── models/
│   │   └── schemas.py          # 요청/응답 Pydantic 스키마
│   ├── routers/
│   │   ├── chat.py             # 채팅 관련 엔드포인트
│   │   └── documents.py        # 문서 관련 엔드포인트
│   └── services/
│       ├── document_loader.py  # 파일 형식별 텍스트 추출
│       ├── vector_store.py     # ChromaDB 저장/검색/삭제
│       └── rag_service.py      # RAG 파이프라인 + 세션 이력 관리
├── static/
│   ├── index.html              # 웹 UI 메인 페이지
│   ├── style.css               # UI 스타일
│   └── app.js                  # API 연동 및 UI 동작 로직
├── documents/                  # 업로드된 파일 저장 디렉토리
├── chroma_db/                  # ChromaDB 벡터 저장소
└── requirements.txt
```

---

## 지원 파일 형식

| 형식 | 확장자 | 비고 |
|------|--------|------|
| PDF | `.pdf` | 텍스트 및 표 추출 |
| Word | `.docx`, `.doc` | 본문 및 표 추출 |
| Excel | `.xlsx`, `.xls` | 모든 시트, 셀 데이터 추출 |
| 한글 | `.hwp` | pyhwp 라이브러리 사용 |

---

## 설치 및 실행

### 1. Ollama 설치 및 모델 다운로드

```bash
# Ollama 설치 (Linux/Mac)
curl -fsSL https://ollama.com/install.sh | sh

# Windows: https://ollama.com 에서 설치 파일 다운로드

# Llama 3.1 8B 모델 다운로드 (약 4.7GB)
ollama pull llama3.1:8b

# Ollama 서버 실행
ollama serve
```

> Ollama가 실행 중이어야 API 서버가 정상 동작합니다.

### 2. Python 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. API 서버 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

실행 후 접속 주소:

| 주소 | 설명 |
|------|------|
| `http://localhost:8000` | 웹 UI |
| `http://localhost:8000/docs` | Swagger API 문서 |
| `http://localhost:8000/health` | 서버 상태 확인 |

---

## 웹 UI 사용법

`http://localhost:8000` 접속 시 아래 화면이 표시됩니다.

```
┌──────────────────┬────────────────────────────────────┐
│   문서 관리      │      🦙 Llama 3.1 RAG 채팅         │
│                  │                                    │
│  [파일 업로드]   │  안녕하세요! 문서를 업로드한 뒤    │
│  (드래그앤드롭)  │  질문해 주세요.                    │
│                  │                                    │
│  📄 파일1.pdf ✕  │  ── 사용자: 주요 내용은? ──────   │
│  📄 파일2.hwp ✕  │  ── AI: ... (출처: 파일1.pdf) ──  │
│                  │                                    │
│                  │  [질문을 입력하세요...]    [전송]  │
└──────────────────┴────────────────────────────────────┘
```

### 문서 업로드
- 왼쪽 패널의 업로드 영역을 **클릭**하거나 파일을 **드래그앤드롭**
- 업로드 완료 시 청크 수와 함께 알림 표시
- 지원 형식: PDF · DOCX · XLSX · HWP

### 채팅
- 오른쪽 패널 하단 입력창에 질문 입력 후 **전송** 또는 **Enter**
- `Shift + Enter`로 줄바꿈 가능
- 답변 하단에 **참고 문서 출처** 표시
- **새 대화** 버튼으로 대화 이력 초기화

### 문서 삭제
- 문서 목록에서 **✕ 버튼** 클릭 → 확인 후 삭제
- 삭제 시 벡터 DB에서도 함께 제거

---

## REST API 사용법

### 문서 업로드

```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@your_document.pdf"
```

응답:
```json
{
  "doc_id": "uuid-...",
  "filename": "your_document.pdf",
  "file_type": "pdf",
  "chunk_count": 42
}
```

### 문서 목록 조회

```bash
curl http://localhost:8000/documents
```

응답:
```json
{
  "documents": [
    {
      "doc_id": "uuid-...",
      "filename": "your_document.pdf",
      "file_type": "pdf",
      "chunk_count": 42
    }
  ],
  "total": 1
}
```

### 문서 삭제

```bash
curl -X DELETE http://localhost:8000/documents/{doc_id}
```

### 채팅 (첫 질문)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "문서의 주요 내용을 알려줘"}'
```

응답:
```json
{
  "answer": "...",
  "sources": ["your_document.pdf"],
  "session_id": "uuid-..."
}
```

### 채팅 (이어서 대화)

`session_id`를 포함하면 이전 대화 맥락을 유지합니다 (최근 5턴).

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "더 자세히 설명해줘", "session_id": "uuid-..."}'
```

### 대화 이력 초기화

```bash
curl -X DELETE http://localhost:8000/chat/session/{session_id}
```

---

## 설정 변경

프로젝트 루트에 `.env` 파일을 생성하여 설정을 변경할 수 있습니다.

```env
# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# 임베딩 모델
EMBEDDING_MODEL=jhgan/ko-sroberta-multitask

# 문서 청크 설정
CHUNK_SIZE=500        # 청크당 최대 문자 수
CHUNK_OVERLAP=50      # 청크 간 겹치는 문자 수

# 검색 설정
RETRIEVER_K=5         # 질문당 검색할 청크 수

# 저장 경로
CHROMA_PERSIST_DIR=./chroma_db
UPLOAD_DIR=./documents
```

### 주요 설정 가이드

| 설정 | 기본값 | 조정 시기 |
|------|--------|----------|
| `CHUNK_SIZE` | 500 | 문서가 길고 세밀한 검색이 필요할 때 줄임 |
| `RETRIEVER_K` | 5 | 답변 품질이 낮을 때 늘림 (속도 저하) |
| `OLLAMA_MODEL` | llama3.1:8b | VRAM 16GB 이상이면 `llama3.1:70b` 가능 |

---

## 동작 방식

### 문서 처리 흐름

```
파일 업로드
    ↓
형식별 텍스트 추출 (PDF/DOCX/XLSX/HWP)
    ↓
RecursiveCharacterTextSplitter로 청크 분할
(chunk_size=500, overlap=50)
    ↓
ko-sroberta-multitask로 벡터 임베딩
    ↓
ChromaDB에 메타데이터(파일명, doc_id)와 함께 저장
```

### 질문-답변 흐름

```
사용자 질문
    ↓
질문을 벡터로 변환
    ↓
ChromaDB에서 유사도 높은 청크 top-K 검색
    ↓
[이전 대화 이력] + [검색된 청크] + [질문]으로 프롬프트 구성
    ↓
Ollama(Llama 3.1 8B)에 전달
    ↓
한국어 답변 + 출처 파일명 반환
```
