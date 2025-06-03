from typing import Union
from fastapi import HTTPException
from sqlmodel import Session
from app.models.exam import Exams
from app.database.database import engine
from sqlalchemy.exc import IntegrityError
from app.schemas.exam import CreateExam, ExamResponse, to_exam_model, to_exam_response

class ExamService:
    @staticmethod
    def create_exam(exam: Union[CreateExam, dict]) -> ExamResponse:
        # Convertir a CreateExam si es un diccionario
        if isinstance(exam, dict):
            try:
                exam = CreateExam(**exam)
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"Invalid input: {str(e)}")

        with Session(engine) as session:
            exam_model = to_exam_model(exam)
            session.add(exam_model)
            try:
                session.commit()
                session.refresh(exam_model)
                return to_exam_response(exam_model)
            except IntegrityError as e:
                session.rollback()
                if "foreign key" in str(e.orig).lower():
                    raise HTTPException(status_code=400, detail="Foreign Key Error: The Child or Doctor does not exist")
                raise HTTPException(status_code=400, detail="Error de integridad en la base de datos.")
