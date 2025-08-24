from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import Optional, List

from app.models.advisor_child import AdvisorChildLink



class Advisor(SQLModel, table=True):
    __tablename__ = "advisors"
    id: str = Field(primary_key=True)
    name: str
    last_name: str
    phone_number: str
    email: str
    children_links: List["AdvisorChildLink"] = Relationship(back_populates="advisor")
    children: List["Children"] = Relationship(
        back_populates="advisors",
        link_model=AdvisorChildLink
    )
