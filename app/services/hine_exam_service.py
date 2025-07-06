from typing import Dict, Any, Optional
from sqlmodel import Session, text
from fastapi import HTTPException, status

# Importaciones de servicios
from app.mappers.exam_mapper import to_exam_response
from app.services.exam_service import ExamService
from app.services.section_service import SectionService
from app.services.item_service import ItemService

# Importaciones de esquemas
from app.schemas.hine_exam import HineExam
from app.schemas.exam import CreateExam
from app.schemas.section import CreateSection
from app.schemas.item import CreateItem

# Database
from app.database.database import engine

class HineExamService:
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
        if not hine_exam.children_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Child ID is required"
            )
        if not hine_exam.doctor_id:
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

                return to_exam_response(rows)
                
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al obtener detalles del examen: {str(e)}"
                )
        
    def get_exams_by_children(self, children_id: str) -> Dict[str, Any]:
        pass


    def create_exam(self, hine_exam: HineExam) -> Dict[str, Any]:
        """
        Crea un examen HINE completo con todas sus secciones e ítems.
        
        Args:
            hine_exam: Datos del examen HINE a crear
            
        Returns:
            Dict con mensaje de éxito y ID del examen creado
            
        Raises:
            HTTPException: Si ocurre algún error durante el proceso
        """
        self._validate_required_fields(hine_exam)

        session = None
        try:
            session = Session(engine)
            
            # Crear el examen principal
            exam_data = CreateExam(
                name="Hine Exam",
                eliminated=False,
                description=hine_exam.general_description,
                child_id=hine_exam.children_id,
                doctor_id=hine_exam.doctor_id
            )
            exam = self.exam_service.create_exam(exam_data)

            # Diccionario para mantener las secciones creadas
            sections = {
                "cranial_nerves": self._create_section(exam.id, "pares craneales"),
                "posture": self._create_section(exam.id, "postura"),
                "movement": self._create_section(exam.id, "movimiento"),
                "tone": self._create_section(exam.id, "tono"),
                "reflexes_reactions": self._create_section(exam.id, "reflejos y reacciones"),
                "motor_milestones": self._create_section(exam.id, "hitos motores"),
                "behavior": self._create_section(exam.id, "comportamiento")
            }

            # Crear todos los ítems para cada sección
            self._create_all_items(sections, hine_exam)

            session.commit()
            return {
                "message": "HINE exam created successfully",
                "exam_id": exam.id,
                "sections": {k: v.id for k, v in sections.items()}
            }

        except HTTPException as e:
            if session:
                session.rollback()
            raise e
        except Exception as e:
            if session:
                session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}"
            )
        finally:
            if session:
                session.close()

    

    def _create_section(self, exam_id: int, section_name: str) -> Any:
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
        try:
            section_data = CreateSection(
                section_name=section_name,
                id_exam=exam_id
            )
            return self.section_service.create_section(section_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error creating section '{section_name}': {str(e)}"
            )

    def _create_all_items(self, sections: Dict[str, Any], hine_exam: HineExam) -> None:
        """
        Crea todos los ítems para todas las secciones del examen.
        
        Args:
            sections: Diccionario con las secciones creadas
            hine_exam: Datos del examen HINE
            
        Raises:
            HTTPException: Si hay un error al crear algún ítem
        """
        # Ítems para pares craneales
        self._create_cranial_nerves_items(sections["cranial_nerves"].id, hine_exam)
        
        # Ítems para postura
        self._create_posture_items(sections["posture"].id, hine_exam)
        
        # Ítems para movimiento
        self._create_movement_items(sections["movement"].id, hine_exam)
        
        # Ítems para tono
        self._create_tone_items(sections["tone"].id, hine_exam)
        
        # Ítems para reflejos y reacciones
        self._create_reflexes_reactions_items(sections["reflexes_reactions"].id, hine_exam)
        
        # Ítems para hitos motores
        self._create_motor_milestones_items(sections["motor_milestones"].id, hine_exam)
        
        # Ítems para comportamiento
        self._create_behavior_items(sections["behavior"].id, hine_exam)

    # Métodos específicos para crear ítems de cada sección (se mantienen igual)
    def _create_cranial_nerves_items(self, section_id: int, hine_exam: HineExam) -> None:
        items = [
            # Apariencia facial
            ("apariencia facial", 
            hine_exam.cranial_nerves_simple_appearance_score,
            hine_exam.cranial_nerves_simple_appearance_description,
            hine_exam.cranial_nerves_simple_appearance_r_asimetric_count,
            hine_exam.cranial_nerves_simple_appearance_l_asimetric_count),
            
            # Movimientos oculares
            ("movimientos oculares",
            hine_exam.cranial_nerves_eye_movement_score,
            hine_exam.cranial_nerves_eye_movement_description,
            hine_exam.cranial_nerves_eye_movement_r_asimetric_count,
            hine_exam.cranial_nerves_eye_movement_l_asimetric_count),
            
            # Respuesta visual
            ("respuesta visual",
            hine_exam.cranial_nerves_visual_response_score,
            hine_exam.cranial_nerves_visual_response_description,
            hine_exam.cranial_nerves_visual_response_r_asimetric_count,
            hine_exam.cranial_nerves_visual_response_l_asimetric_count),
            
            # Respuesta auditiva
            ("respuesta auditiva",
            hine_exam.cranial_nerves_auditory_response_score,
            hine_exam.cranial_nerves_auditory_response_description,
            hine_exam.cranial_nerves_auditory_response_r_asimetric_count,
            hine_exam.cranial_nerves_auditory_response_l_asimetric_count),
            
            # Succión/Deglución
            ("succión / deglución",
            hine_exam.cranial_nerves_sucking_swallowing_score,
            hine_exam.cranial_nerves_sucking_swallowing_description,
            hine_exam.cranial_nerves_sucking_swallowing_r_asimetric_count,
            hine_exam.cranial_nerves_sucking_swallowing_l_asimetric_count)
        ]

        for title, score, description, r_count, l_count in items:
            try:
                self._create_item(
                    section_id=section_id,
                    title=title,
                    score=score,
                    description=description,
                    right_asimetric_count=r_count,
                    left_asimetric_count=l_count
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Error al crear ítem '{title}': {str(e)}"
                )

    def _create_posture_items(self, section_id: int, hineExam: HineExam) -> None:
        """Create items for posture section."""
        items = [
            ("cabeza", hineExam.posture_head_score, hineExam.posture_head_description,
             hineExam.posture_head_r_asimetric_count, hineExam.posture_head_l_asimetric_count),
            ("tronco", hineExam.posture_trunk_score, hineExam.posture_trunk_description,
             hineExam.posture_trunk_r_asimetric_count, hineExam.posture_trunk_l_asimetric_count),
            ("brazos", hineExam.posture_arms_score, hineExam.posture_arms_description,
             hineExam.posture_arms_r_asimetric_count, hineExam.posture_arms_l_asimetric_count),
            ("manos", hineExam.posture_hands_score, hineExam.posture_hands_description,
             hineExam.posture_hands_r_asimetric_count, hineExam.posture_hands_l_asimetric_count),
            ("piernas", hineExam.posture_legs_score, hineExam.posture_legs_description,
             hineExam.posture_legs_r_asimetric_count, hineExam.posture_legs_l_asimetric_count),
            ("pies", hineExam.posture_feet_score, hineExam.posture_feet_description,
             hineExam.posture_feet_r_asimetric_count, hineExam.posture_feet_l_asimetric_count)
        ]

        for title, score, description, r_count, l_count in items:
            self._create_item(section_id, title, score, description, r_count, l_count)

    def _create_movement_items(self, section_id: int, hineExam: HineExam) -> None:
        """Create items for movement section."""
        items = [
            ("cantidad", hineExam.movement_amount_score, hineExam.movement_amount_description,
             hineExam.movement_amount_r_asimetric_count, hineExam.movement_amount_l_asimetric_count),
            ("calidad", hineExam.movement_quality_score, hineExam.movement_quality_description,
             hineExam.movement_quality_r_asimetric_count, hineExam.movement_quality_l_asimetric_count)
        ]

        for title, score, description, r_count, l_count in items:
            self._create_item(section_id, title, score, description, r_count, l_count)

    def _create_tone_items(self, section_id: int, hineExam: HineExam) -> None:
        """Create items for tone section."""
        items = [
            ("signo de la bufanda", hineExam.tone_scarf_sign_score, hineExam.tone_scarf_sign_description,
             hineExam.tone_scarf_sign_r_asimetric_count, hineExam.tone_scarf_sign_l_asimetric_count),
            ("elevacion pasiva del hombro", hineExam.tone_passive_shoulder_elevation_score,
             hineExam.tone_passive_shoulder_elevation_description,
             hineExam.tone_passive_shoulder_elevation_r_asimetric_count,
             hineExam.tone_passive_shoulder_elevation_l_asimetric_count),
            ("pronacion / supinacion", hineExam.tone_pronation_supination_score,
             hineExam.tone_pronation_supination_description,
             hineExam.tone_pronation_supination_r_asimetric_count,
             hineExam.tone_pronation_supination_l_asimetric_count),
            ("aductores de cadera", hineExam.tone_hip_adduction_score,
             hineExam.tone_hip_adduction_description,
             hineExam.tone_hip_adduction_r_asimetric_count,
             hineExam.tone_hip_adduction_l_asimetric_count),
            ("angulo popliteo", hineExam.tone_popliteal_angle_score,
             hineExam.tone_popliteal_angle_description,
             hineExam.tone_popliteal_angle_r_asimetric_count,
             hineExam.tone_popliteal_angle_l_asimetric_count),
            ("dorsiflexion de tobillo", hineExam.tone_ankle_dorsiflexion_score,
             hineExam.tone_ankle_dorsiflexion_description,
             hineExam.tone_ankle_dorsiflexion_r_asimetric_count,
             hineExam.tone_ankle_dorsiflexion_l_asimetric_count),
            ("pull to sit", hineExam.tone_pull_to_sit_score,
             hineExam.tone_pull_to_sit_description,
             hineExam.tone_pull_to_sit_r_asimetric_count,
             hineExam.tone_pull_to_sit_l_asimetric_count),
            ("suspension ventral", hineExam.tone_ventral_suspension_score,
             hineExam.tone_ventral_suspension_description,
             hineExam.tone_ventral_suspension_r_asimetric_count,
             hineExam.tone_ventral_suspension_l_asimetric_count)
        ]

        for title, score, description, r_count, l_count in items:
            self._create_item(section_id, title, score, description, r_count, l_count)

    def _create_reflexes_reactions_items(self, section_id: int, hineExam: HineExam) -> None:
        """Create items for reflexes and reactions section."""
        items = [
            ("proteccion del brazo", hineExam.reflexes_reactions_arm_protecting_score,
             hineExam.reflexes_reactions_arm_protecting_description,
             hineExam.reflexes_reactions_arm_protecting_r_asimetric_count,
             hineExam.reflexes_reactions_arm_protecting_l_asimetric_count),
            ("suspension vertical", hineExam.reflexes_reactions_vertical_suspension_score,
             hineExam.reflexes_reactions_vertical_suspension_description,
             hineExam.reflexes_reactions_vertical_suspension_r_asimetric_count,
             hineExam.reflexes_reactions_vertical_suspension_l_asimetric_count),
            ("suspension lateral", hineExam.reflexes_reactions_lateral_suspension_score,
             hineExam.reflexes_reactions_lateral_suspension_description,
             hineExam.reflexes_reactions_lateral_suspension_r_asimetric_count,
             hineExam.reflexes_reactions_lateral_suspension_l_asimetric_count),
            ("paracaidas", hineExam.reflexes_reactions_parachute_score,
             hineExam.reflexes_reactions_parachute_description,
             hineExam.reflexes_reactions_parachute_r_asimetric_count,
             hineExam.reflexes_reactions_parachute_l_asimetric_count),
            ("reflejos tendinosos", hineExam.reflexes_reactions_tendon_reflexes_score,
             hineExam.reflexes_reactions_tendon_reflexes_description,
             hineExam.reflexes_reactions_tendon_reflexes_r_asimetric_count,
             hineExam.reflexes_reactions_tendon_reflexes_l_asimetric_count)
        ]

        for title, score, description, r_count, l_count in items:
            self._create_item(section_id, title, score, description, r_count, l_count)

    def _create_motor_milestones_items(self, section_id: int, hineExam: HineExam) -> None:
        """Create items for motor milestones section."""
        items = [
            ("control cefalico", hineExam.motor_milestones_head_control_age_achieved,
             hineExam.motor_milestones_head_control_observation,
             hineExam.motor_milestones_head_control_observation_r_asimetric_count,
             hineExam.motor_milestones_head_control_observation_l_asimetric_count),
            
            ("sedestacion", hineExam.motor_milestones_sitting_age_achieved,
             hineExam.motor_milestones_sitting_observation,
             hineExam.motor_milestones_sitting_observation_r_asimetric_count,
             hineExam.motor_milestones_sitting_observation_l_asimetric_count),
            
            ("agarre voluntario", hineExam.motor_milestones_voluntary_gasping_age_achieved,
             f"Lado: {hineExam.motor_milestones_voluntary_gasping_side}\n{hineExam.motor_milestones_voluntary_gasping_observation}",
             hineExam.motor_milestones_voluntary_gasping_observation_r_asi_count,
             hineExam.motor_milestones_voluntary_gasping_observation_l_asi_count),
            
            ("patalear en supino", hineExam.motor_milestones_ability_to_kick_supine_age_achieved,
             hineExam.motor_milestones_ability_to_kick_supine_observation,
             hineExam.motor_milestones_ability_to_kick_supine_obs_r_asi_count,
             hineExam.motor_milestones_ability_to_kick_supine_obs_l_asi_count),
            
            ("volteo", hineExam.motor_milestones_rolling_over_age_achieved,
             f"Lado: {hineExam.motor_milestones_rolling_over_side}\n{hineExam.motor_milestones_rolling_over_observation}",
             hineExam.motor_milestones_rolling_over_observation_r_asimetric_count,
             hineExam.motor_milestones_rolling_over_observation_l_asimetric_count),
            
            ("gateo", hineExam.motor_milestones_crawling_age_achieved,
             f"Arrastra las Nalgas: {hineExam.motor_milestones_crawling_scooting_on_the_bottom}\n{hineExam.motor_milestones_crawling_observation}",
             hineExam.motor_milestones_crawling_observation_r_asimetric_count,
             hineExam.motor_milestones_crawling_observation_l_asimetric_count),
            
            ("bipedestacion", hineExam.motor_milestones_bipedalism_age_achieved,
             hineExam.motor_milestones_bipedalism_observation,
             hineExam.motor_milestones_bipedalism_observation_r_asimetric_count,
             hineExam.motor_milestones_bipedalism_observation_l_asimetric_count),
            
            ("marcha", hineExam.motor_milestones_gait_age_achieved,
             hineExam.motor_milestones_gait_observation,
             hineExam.motor_milestones_gait_observation_r_asimetric_count,
             hineExam.motor_milestones_gait_observation_l_asimetric_count)
        ]

        for title, score, description, r_count, l_count in items:
            self._create_item(section_id, title, score, description, r_count, l_count)

    def _create_behavior_items(self, section_id: int, hineExam: HineExam) -> None:
        """Create items for behavior section."""
        items = [
            ("estado de consciencia", hineExam.behavior_state_of_consciousness_score,
             hineExam.behavior_state_of_consciousness_description, None, None),
            
            ("estado emocional", hineExam.behavior_emotional_state_score,
             hineExam.behavior_emotional_state_description, None, None),
            
            ("interaccion social", hineExam.behavior_social_interaction_score,
             hineExam.behavior_social_interaction_description, None, None)
        ]

        for title, score, description, r_count, l_count in items:
            self._create_item(section_id, title, score, description, r_count, l_count)