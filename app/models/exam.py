from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import Optional, List
class Exams(SQLModel, table=True):
    __tablename__ = "exams"

    id: UUID = Field(default_factory=uuid4,primary_key=True)
    name: str #TODO: NO VA
    created_at: date = Field(default_factory=date.today)
    eliminated: Optional[bool] = Field(default=False)
    gestational_age: str
    cronological_age: str
    corrected_age: str
    head_circumference: str
    
    # Foreign keys
    child_id: str = Field(foreign_key="children.id")
    doctor_id: str = Field(foreign_key="doctors.id")

    # Relationships usando nombres en cadena
    child: Optional["Children"] = Relationship(back_populates="exams")
    doctor: Optional["Doctors"] = Relationship(back_populates="doctor_exams")
    sections: List["Sections"] = Relationship(back_populates="exam")