# schemas/child.py
from pydantic import BaseModel,  ConfigDict
from datetime import date
from typing import Optional
from app.models.exam import Exams

class CreateExam(BaseModel):
    name: str
    eliminated: Optional[bool]
    description: str 
    child_id: str 
    doctor_id: str
    model_config = ConfigDict(from_attributes=True)


class ExamResponse(BaseModel):
    id: int
    name: str
    created_at: date 
    eliminated: bool
    description: str 

    # Foreign keys
    child_id: str 
    doctor_id: str

    model_config = ConfigDict(from_attributes=True)
    

def to_exam_model(exam_create: CreateExam) -> Exams:
    return Exams(**exam_create.model_dump()) 

def to_exam_response(exam: Exams) -> ExamResponse:
    return ExamResponse.model_validate(exam)
