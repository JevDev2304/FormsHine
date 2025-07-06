from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.exam import HineExam
from app.schemas.section import CreateSection
from app.schemas.item import CreateItem
from app.services.hine_exam_service import HineExamService
from app.auth.auth_utils import get_current_user

router = APIRouter()
service = HineExamService()

@router.post("/", response_model=HineExam, status_code=status.HTTP_201_CREATED)
async def create_hine_exam(exam: HineExam, current_user: dict = Depends(get_current_user)):
    try:
        return service.create_exam(exam)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{exam_id}", response_model=HineExam)
async def get_hine_exam(exam_id: str, current_user: dict = Depends(get_current_user)):
    try:
        return service.get_exam(exam_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
@router.get("/children/{children_id}")
async def get_hine_exams_by_children(children_id: str, current_user: dict = Depends(get_current_user)):
    try:
        return service.get_exams_by_children(children_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)




