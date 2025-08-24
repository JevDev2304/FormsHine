from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import Optional, List

# Tabla intermedia para la relación muchos a muchos
class AdvisorChildLink(SQLModel, table=True):
    __tablename__ = "advisor_children"

    advisor_id: str = Field(foreign_key="advisors.id", primary_key=True)
    child_id: str = Field(foreign_key="children.id", primary_key=True)
    relationship: str
    advisor: Optional["Advisor"] = Relationship(back_populates="children_links")
    child: Optional["Children"] = Relationship(back_populates="advisors_links")