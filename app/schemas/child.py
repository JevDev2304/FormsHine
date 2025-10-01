# schemas/child.py
from typing import Optional
from pydantic import BaseModel,  ConfigDict
from datetime import date
from app.models.child import Children as Child

class ChildResponse(BaseModel):
    id: str
    name: str
    last_name: str
    birth_date: date
    exam_date: date

    model_config = ConfigDict(from_attributes=True)

class ChildCreate(BaseModel):
    id: str
    name: str
    last_name: str
    birth_date: date
    exam_date: date

class ChildUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    exam_date: Optional[date] = None

    
def to_child_response(child: Child) -> ChildResponse:
    return ChildResponse.model_validate(child)

def to_child_response_list(children: list[Child]) -> list[ChildResponse]:
    return [ChildResponse.model_validate(child) for child in children]

def to_child_model(child_create: ChildCreate) -> Child:
    return Child(**child_create.model_dump()) 
