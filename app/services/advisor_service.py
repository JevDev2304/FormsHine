from fastapi import HTTPException
from sqlmodel import Session, select
from app.database.database import engine

from app.models.advisor import Advisor
from app.models.advisor_child import AdvisorChildLink
from app.models.child import Children
from app.schemas.advisor import AdvisorCreate, AdvisorResponse, AdvisorUpdate, to_advisor_model, to_advisor_response


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
                raise HTTPException(
                    status_code=400,
                    detail=f"Advisor with ID {advisor_create.id} already exists. Use update_advisor instead."
                )

            # Crear un nuevo advisor
            advisor = to_advisor_model(advisor_create)
            session.add(advisor)

            # Crear el vínculo inicial con ese niño
            link = AdvisorChildLink(
                advisor_id=advisor.id,
                child_id=child.id,
                relationship=advisor_create.relationship
            )
            session.add(link)

            session.commit()
            session.refresh(advisor)
            return to_advisor_response(advisor)

    @staticmethod
    def update_advisor(advisor_update: AdvisorUpdate) -> AdvisorResponse:
        with Session(engine) as session:
            child = session.get(Children, advisor_update.child_id)
            if not child:
                raise HTTPException(
                    status_code=404,
                    detail=f"Child with ID {advisor_update.child_id} not found."
                )

            advisor = session.get(Advisor, advisor_update.id)

            if not advisor:
                raise HTTPException(
                    status_code=404,
                    detail=f"Advisor with ID {advisor_update.id} not found. Use create_advisor instead."
                )

            # Actualizar solo los campos que vengan en la request
            if advisor_update.name is not None:
                advisor.name = advisor_update.name
            if advisor_update.last_name is not None:
                advisor.last_name = advisor_update.last_name
            if advisor_update.phone_number is not None:
                advisor.phone_number = advisor_update.phone_number
            if advisor_update.email is not None:
                advisor.email = advisor_update.email

            # Verificar si ya existe el vínculo con ese niño
            statement = select(AdvisorChildLink).where(
                AdvisorChildLink.advisor_id == advisor.id,
                AdvisorChildLink.child_id == child.id
            )
            link = session.exec(statement).first()

            if link:
                raise HTTPException(
                    status_code=400,
                    detail=f"Advisor with ID {advisor_update.id} already linked to Child with ID {advisor_update.child_id}."
                )

            link = AdvisorChildLink(
                advisor_id=advisor.id,
                child_id=child.id,
                relationship=advisor_update.relationship
            )
            session.add(link)

            session.commit()
            session.refresh(advisor)
            return to_advisor_response(advisor)

