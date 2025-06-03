# schemas/child.py
from pydantic import BaseModel,  ConfigDict
from datetime import date
from app.models.child import Children as Child

class ChildResponse(BaseModel):
    id: str
    name: str
    last_name: str
    gestational_age: int
    head_circumference: float
    birth_date: date
    document_type: str

    model_config = ConfigDict(from_attributes=True)

class ChildCreate(BaseModel):
    id: str
    name: str
    last_name: str
    gestational_age: int
    head_circumference: float
    birth_date: date
    document_type: str = "Registro"

def to_child_response(child: Child) -> ChildResponse:
    return ChildResponse.model_validate(child)

def to_child_response_list(children: list[Child]) -> list[ChildResponse]:
    return [ChildResponse.model_validate(child) for child in children]

def to_child_model(child_create: ChildCreate) -> Child:
    return Child(**child_create.model_dump()) 
