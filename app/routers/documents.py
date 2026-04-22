import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.models.schemas import DeleteResponse, DocumentInfo, DocumentListResponse
from app.services.document_loader import SUPPORTED_EXTENSIONS, load_document
from app.services.vector_store import add_document, delete_document, list_documents

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentInfo, summary="문서 업로드 및 벡터 저장")
async def upload_document(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    save_path = upload_dir / file.filename

    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        text = load_document(str(save_path))
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"문서 파싱 실패: {str(e)}")

    if not text.strip():
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="문서에서 텍스트를 추출할 수 없습니다.")

    doc_id, chunk_count = add_document(text, file.filename, ext.lstrip("."))

    return DocumentInfo(
        doc_id=doc_id,
        filename=file.filename,
        file_type=ext.lstrip("."),
        chunk_count=chunk_count,
    )


@router.get("", response_model=DocumentListResponse, summary="업로드된 문서 목록 조회")
async def get_documents():
    docs = list_documents()
    return DocumentListResponse(
        documents=[DocumentInfo(**d) for d in docs],
        total=len(docs),
    )


@router.delete("/{doc_id}", response_model=DeleteResponse, summary="문서 삭제")
async def remove_document(doc_id: str):
    try:
        delete_document(doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 삭제 실패: {str(e)}")
    return DeleteResponse(doc_id=doc_id, message="문서가 삭제되었습니다.")
