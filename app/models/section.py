from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional,List
from app.models.exam import Exams
from app.models.item import Items

class Sections(SQLModel, table=True):
    __tablename__ = "sections"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    section_comments: str
    section_name: str
    
    # Foreign key
    id_exam: UUID = Field(foreign_key="exams.id")

    # Relationship
    exam: Optional["Exams"] = Relationship(back_populates="sections")
    items:  List["Items"] = Relationship(back_populates="section")
