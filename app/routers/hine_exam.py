from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.exam import CreateExam
from app.schemas.section import CreateSection
from app.schemas.item import CreateItem
from app.services.hine_exam_service import HineExamService
from app.schemas.hine_exam import HineExamCreate


router = APIRouter()
service = HineExamService()



@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_hine_exam(exam:HineExamCreate ):
    try:
        return service.create_exam(exam)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
@router.get("/{exam_id}")
async def get_hine_exams(exam_id: int):
    try:
        return service.get_exam(exam_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)




