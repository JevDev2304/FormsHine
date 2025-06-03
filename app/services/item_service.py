from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.item import Items
from app.database.database import engine
from sqlalchemy.exc import IntegrityError
from app.schemas.item import CreateItem, ItemResponse, to_item_model, to_item_response

class ItemService:
    @staticmethod
    def create_item(item: CreateItem) -> ItemResponse:
        with Session(engine) as session:
            item_model = to_item_model(item)
            session.add(item_model)
            try:
                session.commit()
                session.refresh(item_model)
                return to_item_response(item_model)
            except IntegrityError as e:
                session.rollback()
                msg = str(e.orig).lower()
                if "foreign key" in msg:
                    if "section_id" in msg:
                        raise HTTPException(status_code=400, detail="Foreign key error: Section with this ID does not exist.")
                    else:
                        raise HTTPException(status_code=400, detail="Foreign key constraint failed.")
                raise HTTPException(status_code=400, detail="Database integrity error.")
