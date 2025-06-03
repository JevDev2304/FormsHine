from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import Optional, List

class Doctors(SQLModel, table=True):
    __tablename__ = "doctors"
    id: str = Field(primary_key=True)
    name: str
    last_name: str
    birth_date: Optional[date]
    eliminated: Optional[bool] = Field(default=False)
    password: str

    doctor_exams: List['Exams'] = Relationship(back_populates="doctor")