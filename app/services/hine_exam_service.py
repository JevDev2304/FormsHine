from typing import Dict, Any, List, Optional
from sqlmodel import Session, text
from fastapi import HTTPException, status

# Importaciones de servicios
from app.mappers.exam_mapper import *
from app.services.exam_service import ExamService
from app.services.section_service import SectionService
from app.services.item_service import ItemService

# Importaciones de esquemas
from app.schemas.exam import HineExam
from app.schemas.section import CreateSection, SectionResponse
from app.schemas.item import CreateItem

# Database
from app.database.database import engine

class HineExamService:
    SEPARATOR_SECTION_COMMENTS = "|||"
    def __init__(
        self,
        exam_service: Optional[ExamService] = None,
        section_service: Optional[SectionService] = None,
        item_service: Optional[ItemService] = None
    ):
        """
        Inicializa el servicio con las dependencias inyectadas.
        Si no se proporcionan, se crean instancias por defecto.
        """
        self.exam_service = exam_service or ExamService()
        self.section_service = section_service or SectionService()
        self.item_service = item_service or ItemService()

    def _create_item(
        self,
        section_id: int,
        title: str,
        score: int,
        description: str,
        right_asimetric_count: Optional[int] = None,
        left_asimetric_count: Optional[int] = None
    ) -> Any:
        """
        Crea un ítem usando el modelo Pydantic ItemCreate.
        
        Args:
            section_id: ID de la sección a la que pertenece el ítem
            title: Título del ítem
            score: Puntuación del ítem
            description: Descripción del ítem
            right_asimetric_count: Conteo asimétrico derecho (opcional)
            left_asimetric_count: Conteo asimétrico izquierdo (opcional)
            
        Returns:
            El ítem creado
            
        Raises:
            HTTPException: Si hay un error al crear el ítem
        """
        try:
            item_data = CreateItem(
                title=title,
                score=score,
                description=description,
                right_asimetric_count=right_asimetric_count,
                left_asimetric_count=left_asimetric_count,
                section_id=section_id
            )
            return self.item_service.create_item(item_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error creating item '{title}': {str(e)}"
            )

    def _validate_required_fields(self, hine_exam: HineExam) -> None:
        """
        Valida los campos requeridos antes de procesar el examen.
        
        Args:
            hine_exam: Datos del examen a validar
            
        Raises:
            HTTPException: Si faltan campos requeridos
        """
        if not hine_exam.patientId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Child ID is required"
            )
        if not hine_exam.userId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor ID is required"
            )
            
    def get_exam(self, exam_id: str) -> HineExam:
        with Session(engine) as session:
            try:
                # Consulta a la vista modificada
                sql = text("""
                    SELECT * FROM full_exam_view
                    WHERE exam_id = :exam_id
                    ORDER BY section_id, item_id
                """)
                
                result = session.exec(sql.bindparams(exam_id=exam_id))
                rows = result.all()
                
                if not rows:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Examen con ID {exam_id} no encontrado"
                    )

                return to_exam_response_from_rows(rows)
                
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al obtener detalles del examen: {str(e)}"
                )
        
    def get_exams_by_children(self, child_id: str) -> List[HineExam]:
        with Session(engine) as session:
            try:
                # Consulta a la vista modificada
                sql = text("""
                    SELECT * FROM full_exam_view
                    WHERE child_id = :child_id
                    ORDER BY section_id, item_id
                """)
                
                result = session.exec(sql.bindparams(child_id=child_id))
                rows = result.all()
                
                if not rows:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Niño con ID {child_id} no encontrado"
                    )

                return build_exams_from_rows(rows)
                
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al obtener detalles del examen: {str(e)}"
                )


    def create_exam(self, hine_exam: HineExam) -> HineExam:
        self._validate_required_fields(hine_exam)

        session = None
        try:
            session = Session(engine)

            created_exam = self.exam_service.create_exam(hine_exam)

            # Crear secciones y asignar ítems
            section_ids = {}

            for module in hine_exam.analysis.modules:
                #TODO: cambiar hine_exam.id al id creado si lo genero yo
                section = self._create_section(created_exam.id, "analysis:"+module.moduleId, hine_exam.analysis.generalComments)

                section_ids[module.moduleId] = section.id

                for item in module.responses:
                    self._create_item(
                        section_id=section.id,
                        title=item.questionId,
                        score=item.selectedValue,
                        description=item.comment,
                        left_asimetric_count=int(item.leftAsymmetry),
                        right_asimetric_count=int(item.rightAsymmetry)
                    )

            # Motor milestones
            motor_section = self._create_section(created_exam.id, "motor_milestones", section_comments=hine_exam.motorMilestones.generalComments)
            for item in hine_exam.motorMilestones.responses:
                self._create_item(
                    section_id=motor_section.id,
                    title=item.questionId,
                    score=item.selectedValue,
                    description=item.comment,
                    left_asimetric_count=int(item.leftAsymmetry),
                    right_asimetric_count=int(item.rightAsymmetry)
                )

            # Behavior
            behavior_section = self._create_section(created_exam.id, "behavior", section_comments=hine_exam.behavior.generalComments)
            for item in hine_exam.behavior.responses:
                self._create_item(
                    section_id=behavior_section.id,
                    title=item.questionId,
                    score=item.selectedValue,
                    description=item.comment
                )

            session.commit()

            # Obtener el examen recién creado desde la vista para retornar respuesta completa
            sql = text("""
                SELECT * FROM full_exam_view
                WHERE exam_id = :exam_id
                ORDER BY section_id, item_id
            """)
            result = session.exec(sql.bindparams(exam_id=created_exam.id))
            rows = result.all()

            return to_exam_response_from_rows(rows)

        except HTTPException:
            if session:
                session.rollback()
            raise 
        except Exception as e:
            if session:
                session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear el examen: {str(e)}"
            )
        finally:
            if session:
                session.close()

    def _create_section(self, exam_id: str, section_name: str, section_comments: List[str]) -> SectionResponse:
        """
        Método helper para crear una sección con manejo de errores.
        
        Args:
            exam_id: ID del examen al que pertenece la sección
            section_name: Nombre de la sección
            
        Returns:
            La sección creada
            
        Raises:
            HTTPException: Si hay un error al crear la sección
        """
        final_section_comments = self.SEPARATOR_SECTION_COMMENTS.join(section_comments)

        try:
            section_data = CreateSection(
                section_name=section_name,
                id_exam=exam_id,
                section_comments=final_section_comments
            )
            return self.section_service.create_section(section_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error creating section '{section_name}': {str(e)}"
            )