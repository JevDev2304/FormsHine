from fastapi import HTTPException
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from app.models.exam import Exams
from app.schemas.exam import HineExam
from app.database.database import engine
from app.mappers.exam_mapper import to_exam_model

class ExamService:
    @staticmethod
    def create_exam(exam: HineExam) -> Exams:
        # Convertir esquema a modelo
        try:
            exam_model = to_exam_model(exam)
        except Exception as e:
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid input data: {str(e)}"
            )

        # Guardar en base de datos
        try:
            with Session(engine) as session:
                session.add(exam_model)
                session.commit()
                session.refresh(exam_model)
                return exam_model
        except IntegrityError as e:
            if "foreign key" in str(e.orig).lower():
                raise HTTPException(
                    status_code=400, 
                    detail="Foreign key error: The Child or Doctor does not exist"
                )
            raise HTTPException(
                status_code=400, 
                detail="Integrity error: Possible duplicate or constraint violation"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Unexpected error: {str(e)}"
            )
