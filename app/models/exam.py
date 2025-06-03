from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import Optional, List
from app.models.doctor import Doctors
from app.models.section import Sections
class Exams(SQLModel, table=True):
    __tablename__ = "exams"

    id: int = Field(default= None,primary_key=True)
    name: str
    created_at: date = Field(default_factory=date.today)
    eliminated: Optional[bool] = Field(default=False)
    description: str = Field(default=None)

    # Foreign keys
    child_id: str = Field(foreign_key="children.id")
    doctor_id: str = Field(foreign_key="doctors.id")

    # Relationships usando nombres en cadena
    child: Optional["Children"] = Relationship(back_populates="exams")
    doctor: Optional["Doctors"] = Relationship(back_populates="doctor_exams")
    sections: List["Sections"] = Relationship(back_populates="exam")