from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.child import Children as Child
from app.database.database import engine
from sqlalchemy.exc import IntegrityError
from app.schemas.child import ChildResponse, ChildCreate,to_child_response, to_child_response_list , to_child_model


class ChildService:
    @staticmethod
    def create_child(child: ChildCreate) -> ChildResponse:
        with Session(engine) as session:
            try:
                child = to_child_model(child)
                session.add(child)
                session.commit()
                session.refresh(child)
                return to_child_response(child)
            except IntegrityError as e:
                print(e)
                session.rollback()
                raise HTTPException(status_code=409, detail=f"Child with ID {child.id} already exists.")

    @staticmethod
    def get_all_children() -> list[ChildResponse]:
        with Session(engine) as session:
            children = session.exec(
                select(Child).where(Child.eliminated == 0)
            ).all()
            return to_child_response_list(children)

    @staticmethod
    def get_child_by_id(child_id: str) -> ChildResponse | None:
        with Session(engine) as session:
            child = session.exec(
                select(Child).where(Child.id == child_id, Child.eliminated == 0)
            ).first()
            return to_child_response(child) if child else None

    @staticmethod
    def update_child(child_id: str, data: dict) -> ChildResponse | None:
        with Session(engine) as session:
            child = session.exec(
                select(Child).where(Child.id == child_id, Child.eliminated == 0)
            ).first()
            if not child:
                return None
            for key, value in data.items():
                setattr(child, key, value)
            session.commit()
            session.refresh(child)
            return to_child_response(child)

    @staticmethod
    def soft_delete_child(child_id: str) -> bool:
        with Session(engine) as session:
            child = session.exec(
                select(Child).where(Child.id == child_id, Child.eliminated == 0)
            ).first()
            if not child:
                return False
            child.eliminated = 1
            session.commit()
            return True
