from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import Optional, List

from app.models.advisor_child import AdvisorChildLink

class Children(SQLModel, table=True):
    __tablename__ = "children"
    id: str = Field(primary_key=True)
    name: str
    last_name: str
    gestational_age: str
    cronological_age: str
    corrected_age: str
    head_circumference: str
    birth_date: date
    exam_date: date
    eliminated: Optional[int] = Field(default=0)

    exams: List['Exams'] = Relationship(back_populates="child")
    advisors_links: List["AdvisorChildLink"] = Relationship(back_populates="child")
    advisors: List["Advisor"] = Relationship(
        back_populates="children",
        link_model=AdvisorChildLink
    )
