from uuid import UUID
from pydantic import BaseModel,  ConfigDict
from datetime import date
from typing import Optional
from app.models.section import Sections

class CreateSection(BaseModel):
    section_name: str
    id_exam: Optional[UUID]
    model_config = ConfigDict(from_attributes=True)

class SectionResponse(BaseModel):
    id: UUID 
    section_name: str
    id_exam: Optional[UUID]
    model_config = ConfigDict(from_attributes=True)


def to_section_model(section_create: CreateSection) -> Sections:
    return Sections(**section_create.model_dump()) 

def to_section_response(section: Sections) -> SectionResponse:
    return SectionResponse.model_validate(section)
