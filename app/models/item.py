from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import Optional, TYPE_CHECKING


class Items(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    score: int
    description: str
    right_asimetric_count : int = Field(default=0)
    left_asimetric_count: int = Field (default=0)
    # Foreign key
    section_id: UUID = Field(foreign_key="sections.id")

    # Relationship
    section: Optional["Sections"] = Relationship(back_populates="items")
