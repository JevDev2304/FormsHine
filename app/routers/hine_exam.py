from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from typing import List
from io import BytesIO

from app.schemas.exam import HineExam
from app.schemas.section import CreateSection
from app.schemas.item import CreateItem
from app.services.hine_exam_service import HineExamService
from app.auth.auth_utils import get_current_user
from app.services.hine_pdf_renderer import HINEPdfRenderer

router = APIRouter()
service = HineExamService()

@router.post("/", response_model=HineExam, status_code=status.HTTP_201_CREATED)
async def create_hine_exam(exam: HineExam, current_user: dict = Depends(get_current_user)):
    try:
        print(exam)
        return service.create_exam(exam)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{exam_id}", response_model=HineExam)
async def get_hine_exam(exam_id: str, current_user: dict = Depends(get_current_user)):
    try:
        return service.get_exam(exam_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{exam_id}/pdf", response_model=HineExam)
async def get_hine_exam(exam_id: str, current_user: dict = Depends(get_current_user)):
    try:
        pdf_bytes = service.get_exam_pdf(exam_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    filename = f"HINE_Examen_{exam_id}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
    
@router.get("/children/{children_id}")
async def get_hine_exams_by_children(children_id: str, current_user: dict = Depends(get_current_user)):
    try:
        return service.get_exams_by_children(children_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/children/{children_id}/history/pdf")
async def get_hine_history_pdf(children_id: str, current_user: dict = Depends(get_current_user)):
    """
    Devuelve un PDF con TODOS los exámenes HINE del niño (historia clínica).
    """
    try:
        pdf_bytes = service.get_child_history_pdf(children_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    filename = f"HINE_Historia_{children_id}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )