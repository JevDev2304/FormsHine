from sqlmodel import SQLModel, Field, Relationship
from typing import Optional,List
from app.models.item import Items

class Sections(SQLModel, table=True):
    __tablename__ = "sections"
    id: int = Field(default=None, primary_key=True)
    section_name: str
    
    # Foreign key
    id_exam: int = Field(foreign_key="exams.id")

    # Relationship
    exam: Optional["Exams"] = Relationship(back_populates="sections")
    items:  List["Items"] = Relationship(back_populates="section")
