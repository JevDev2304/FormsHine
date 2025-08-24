# schemas/child.py
from pydantic import BaseModel,  ConfigDict
from datetime import date

from app.models.advisor import Advisor

class AdvisorResponse(BaseModel):
    id: str
    name: str
    last_name : str
    phone_number: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class AdvisorCreate(BaseModel):
    id: str
    name: str
    last_name : str
    phone_number: str
    email: str
    child_id: str
    relationship: str

def to_advisor_response(advisor: Advisor) -> AdvisorResponse:
    return AdvisorResponse.model_validate(advisor)

def to_advisor_response_list(advisors: list[Advisor]) -> list[AdvisorResponse]:
    return [AdvisorResponse.model_validate(advisor) for advisor in advisors]

def to_advisor_model(advisor_create: AdvisorCreate) -> Advisor:
    return Advisor(**advisor_create.model_dump()) 
