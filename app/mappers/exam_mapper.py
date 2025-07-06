from typing import Any
from collections import defaultdict
from app.models.exam import Exams
from app.schemas.exam.exam import (
    HineExam,AnalysisData, BehaviorData, MotorMilestoneData,
    ModuleResponse, QuestionResponse, BehaviorResponse
)


def to_exam_model(hine_exam: HineExam) -> Exams:
    """
    Convierte un objeto HineExam (esquema recibido desde el frontend)
    a un modelo Exams que representa la tabla en la base de datos.
    Esta función no incluye la creación de secciones ni ítems asociados.
    """
    return Exams(
        id= hine_exam.examId,
        name="Hine Exam",
        eliminated=False,
        description=hine_exam.description,
        child_id=hine_exam.patientId,
        doctor_id=hine_exam.userId,
        created_at=hine_exam.c
        # created_at se genera automáticamente si no se especifica
    )


def to_exam_response(rows: list[Any]) -> HineExam:
    if not rows:
        raise ValueError("No data found for exam")

    first = rows[0]

    # Acumuladores
    analysis_modules = []
    motor_responses = []
    behavior_responses = []

    analysis_score = 0
    max_score = 0
    total_right = 0
    total_left = 0

    # Agrupar filas por section_name
    sections = defaultdict(list)
    for row in rows:
        sections[row.section_name].append(row)

    # Procesar Analysis (buscando secciones con prefijo 'analysis:')
    for section_key, section_rows in sections.items():
        if section_key.startswith("analysis:"):
            module_id = section_key.split(":")[1]
            module_score = 0
            responses = []

            for row in section_rows:
                responses.append(QuestionResponse(
                    questionId=row.item_title,
                    selectedValue=row.item_score,
                    comment=row.item_description,
                    leftAsymmetry=bool(row.left_asymmetry),
                    rightAsymmetry=bool(row.right_asymmetry),
                ))
                module_score += row.item_score or 0
                max_score += 5
                total_left += row.left_asymmetry or 0
                total_right += row.right_asymmetry or 0

            analysis_modules.append(ModuleResponse(
                moduleId=module_id,
                obtainedScore=module_score,
                responses=responses
            ))
            analysis_score += module_score

    # Procesar motor milestones
    for row in sections.get("motor_milestones", []):
        motor_responses.append(QuestionResponse(
            questionId=row.item_title,
            selectedValue=row.item_score,
            comment=row.item_description,
            leftAsymmetry=bool(row.left_asymmetry),
            rightAsymmetry=bool(row.right_asymmetry),
        ))

    # Procesar behavior
    for row in sections.get("behavior", []):
        behavior_responses.append(BehaviorResponse(
            questionId=row.item_title,
            selectedValue=row.item_score,
            comment=row.item_description,
        ))

    return HineExam(
        examId=first.exam_id,
        patientId=first.child_id,
        userId=first.doctor_id,
        examDate=first.created_at.isoformat(),
        description=first.description,
        analysis=AnalysisData(
            modules=analysis_modules,
            totalScore=analysis_score,
            maxPossibleScore=max_score,
            totalRightAsymmetries=total_right,
            totalLeftAsymmetries=total_left,
        ),
        motorMilestones=MotorMilestoneData(responses=motor_responses),
        behavior=BehaviorData(responses=behavior_responses),
    )
