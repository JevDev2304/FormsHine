from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.exam import Exams
from app.database.database import engine
from sqlalchemy.exc import IntegrityError
from app.schemas.section import CreateSection, SectionResponse, to_section_model, to_section_response

class SectionService:
    @staticmethod
    def create_section(section: CreateSection) -> SectionResponse:
        with Session(engine) as session:
            section_model = to_section_model(section)
            session.add(section_model)
            try:
                session.commit()
                session.refresh(section_model)
                return to_section_response(section_model)
            except IntegrityError as e:
                session.rollback()
                msg = str(e.orig).lower()
                if "foreign key" in msg:
                    if "id_exam" in msg:
                        raise HTTPException(status_code=400, detail="Foreign key error: Exam with this ID does not exist.")
                    else:
                        raise HTTPException(status_code=400, detail="Foreign key constraint failed.")
                raise HTTPException(status_code=400, detail="Database integrity error.")
