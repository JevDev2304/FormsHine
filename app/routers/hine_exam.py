from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.exam import CreateExam
from app.schemas.section import CreateSection
from app.schemas.item import CreateItem
from app.services.hine_exam_service import HineExamService
from app.schemas.hine_exam import HineExamCreate
from app.auth.auth_utils import get_current_user

router = APIRouter()
service = HineExamService()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_hine_exam(exam: HineExamCreate, current_user: dict = Depends(get_current_user)):
    try:
        return service.create_exam(exam)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{exam_id}")
async def get_hine_exams(exam_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return service.get_exam(exam_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)




