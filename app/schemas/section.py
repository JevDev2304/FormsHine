from uuid import UUID
from pydantic import BaseModel,  ConfigDict
from datetime import date
from typing import List, Optional
from app.models.section import Sections

class CreateSection(BaseModel):
    section_comments: str
    section_name: str
    id_exam: Optional[UUID]
    model_config = ConfigDict(from_attributes=True)

class SectionResponse(BaseModel):
    id: UUID 
    section_comments: List[str]
    section_name: str
    id_exam: Optional[UUID]
    model_config = ConfigDict(from_attributes=True)


def to_section_model(section_create: CreateSection) -> Sections:
    return Sections(**section_create.model_dump()) 

def to_section_response(section: Sections) -> SectionResponse:
    from app.services.hine_exam_service import HineExamService
    analysis_general_comments = section.section_comments.split(HineExamService.SEPARATOR_SECTION_COMMENTS)

    return  SectionResponse.model_validate({
    **section.model_dump(),
    "section_comments": analysis_general_comments
})
