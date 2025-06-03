from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import Optional, List

class Children(SQLModel, table=True):
    __tablename__ = "children"
    id: str = Field(primary_key=True)
    name: str
    last_name: str
    gestational_age: int
    head_circumference: float
    birth_date: date
    eliminated: Optional[int] = Field(default=0)
    document_type: str = Field(default="Registro")

    exams: List['Exams'] = Relationship(back_populates="child")
