from typing import Any, List
from collections import defaultdict
from app.models.exam import Exams
from app.schemas.exam import (
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
        child_id=hine_exam.patientId,
        doctor_id=hine_exam.userId,
        gestational_age=hine_exam.gestationalAge,
  cronological_age=hine_exam.cronologicalAge,
  corrected_age=hine_exam.correctedAge,
  head_circumference=hine_exam.headCircumference,
        created_at=hine_exam.examDate
        # created_at se genera automáticamente si no se especifica
    )


def to_exam_response_from_rows(rows: list[Any]) -> HineExam:
    from app.services.hine_exam_service import HineExamService

    if not rows:
        raise ValueError("No data found for exam")

    first = rows[0]

    analysis_general_comments = []
    motor_general_comments = []
    behavior_general_comments = []


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
                comments_raw = row.section_comments or ""
                analysis_general_comments = comments_raw.split(HineExamService.SEPARATOR_SECTION_COMMENTS)
                print("-------------------")
                print(analysis_general_comments)
                responses.append(QuestionResponse(
                    questionId=row.item_title,
                    selectedValue=row.item_score,
                    comment=row.item_description,
                    leftAsymmetry=bool(row.left_asimetric_count),
                    rightAsymmetry=bool(row.right_asimetric_count),
                ))

                module_score += row.item_score or 0
                max_score += 3
                total_left += row.left_asimetric_count or 0
                total_right += row.right_asimetric_count or 0

            analysis_modules.append(ModuleResponse(
                moduleId=module_id,
                obtainedScore=module_score,
                responses=responses
            ))
            analysis_score += module_score

    # Motor milestones
    for row in sections.get("motor_milestones", []):
        comments_raw = row.section_comments or ""
        motor_general_comments = comments_raw.split(HineExamService.SEPARATOR_SECTION_COMMENTS)

        motor_responses.append(QuestionResponse(
            questionId=row.item_title,
            selectedValue=row.item_score,
            comment=row.item_description,
            leftAsymmetry=bool(row.left_asimetric_count),
            rightAsymmetry=bool(row.right_asimetric_count),
        ))

    # Behavior
    for row in sections.get("behavior", []):
        comments_raw = row.section_comments or ""
        behavior_general_comments = comments_raw.split(HineExamService.SEPARATOR_SECTION_COMMENTS)

        behavior_responses.append(BehaviorResponse(
            questionId=row.item_title,
            selectedValue=row.item_score,
            comment=row.item_description,
        ))


    return HineExam(
        examId=first.exam_id,
        patientId=first.child_id,
        userId=first.doctor_id,
        doctorName=first.doctor_name,
        examDate = first.exam_created_at.strftime("%Y-%m-%d"),
        analysis=AnalysisData(
            modules=analysis_modules,
            totalScore=analysis_score,
            maxPossibleScore=max_score,
            totalRightAsymmetries=total_right,
            totalLeftAsymmetries=total_left,
            generalComments=analysis_general_comments
        ),
        motorMilestones=MotorMilestoneData(responses=motor_responses, generalComments=motor_general_comments),
        behavior=BehaviorData(responses=behavior_responses, generalComments=behavior_general_comments),
        gestationalAge=first.gestational_age,
        cronologicalAge=first.cronological_age,
        correctedAge=first.corrected_age,
        headCircumference=first.head_circumference,
    )


def build_exams_from_rows(rows: list[Any]) -> List[HineExam]:
    if not rows:
        return []

    # Agrupar filas por exam_id
    exams_grouped = defaultdict(list)
    for row in rows:
        exams_grouped[row.exam_id].append(row)

    # Convertir cada grupo a un HineExam
    exams: List[HineExam] = []
    for exam_rows in exams_grouped.values():
        exam = to_exam_response_from_rows(exam_rows)
        exams.append(exam)

    exams.sort(key=lambda e: e.examDate, reverse=True)

    return exams
