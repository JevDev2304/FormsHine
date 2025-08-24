from fastapi import HTTPException
from sqlmodel import Session, select
from app.database.database import engine

from app.models.advisor import Advisor
from app.models.advisor_child import AdvisorChildLink
from app.models.child import Children
from app.schemas.advisor import AdvisorCreate, AdvisorResponse, to_advisor_model, to_advisor_response

class AdvisorService:
    @staticmethod
    def create_advisor(advisor_create: AdvisorCreate) -> AdvisorResponse:
        with Session(engine) as session:
            child = session.get(Children, advisor_create.child_id)
            if not child:
                raise HTTPException(
                    status_code=404,
                    detail=f"Child with ID {advisor_create.child_id} not found."
                )

            advisor = session.get(Advisor, advisor_create.id)

            if advisor:
                # Actualizar datos básicos del advisor existente
                advisor.name = advisor_create.name
                advisor.last_name = advisor_create.last_name
                advisor.phone_number = advisor_create.phone_number
                advisor.email = advisor_create.email
            else:
                # Crear un nuevo advisor
                advisor = to_advisor_model(advisor_create)
                session.add(advisor)

            # Verificar si ya existe el vínculo con ese niño
            statement = select(AdvisorChildLink).where(
                AdvisorChildLink.advisor_id == advisor.id,
                AdvisorChildLink.child_id == child.id
            )
            link = session.exec(statement).first()

            if not link:
                # Crear el vínculo si no existía
                link = AdvisorChildLink(
                    advisor_id=advisor.id,
                    child_id=child.id,
                    relationship=advisor_create.relationship
                )
                session.add(link)

            session.commit()
            session.refresh(advisor)
            return to_advisor_response(advisor)
