from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import Optional, TYPE_CHECKING

from app.models.section import Sections



class Items(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    score: int
    description: str
    right_asimetric_count : int = Field(default=0)
    left_asimetric_count: int = Field (default=0)
    # Foreign key
    section_id: int = Field(foreign_key="sections.id")

    # Relationship
    section: Optional["Sections"] = Relationship(back_populates="items")
