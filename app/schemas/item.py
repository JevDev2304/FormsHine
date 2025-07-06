from uuid import UUID
from pydantic import BaseModel,  ConfigDict
from datetime import date
from app.models.item import Items
from typing import Optional

class CreateItem(BaseModel):
    title: str
    score: int
    description: Optional[str] = None
    right_asimetric_count : Optional[int] = 0 
    left_asimetric_count: Optional[int] = 0
    section_id: UUID
    model_config = ConfigDict(from_attributes=True)

class ItemResponse(BaseModel):
    id: UUID 
    title: str
    score: int
    description: str
    right_asimetric_count : int 
    left_asimetric_count: int 
    section_id: UUID
    model_config = ConfigDict(from_attributes=True)


def to_item_model(section_create: CreateItem) -> Items:
    return Items(**section_create.model_dump()) 

def to_item_response(item: Items) -> ItemResponse:
    return ItemResponse.model_validate(item)
