from typing import Dict, Any, List, Optional
from sqlmodel import Session, text
from fastapi import HTTPException, status
from html import escape as html_escape
from weasyprint import HTML

# Importaciones de servicios
from app.mappers.exam_mapper import *
from app.schemas.child import ChildUpdate
from app.services.child_service import ChildService
from app.services.exam_service import ExamService
from app.services.section_service import SectionService
from app.services.item_service import ItemService

# Importaciones de esquemas
from app.schemas.exam import HineExam
from app.schemas.section import CreateSection, SectionResponse
from app.schemas.item import CreateItem

# Database
from app.database.database import engine

childService = ChildService()

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
                sql = text("""
                    SELECT * FROM full_exam_view
                    WHERE exam_id = :exam_id
                    ORDER BY section_id, item_id
                """)
                result = session.exec(sql.bindparams(exam_id=exam_id))
                print(exam_id)
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

    def get_child_history_pdf(self, child_id: str) -> bytes:
        exams = self.get_exams_by_children(child_id)
        if not exams:
            raise HTTPException(status_code=404, detail="No se encontraron exámenes para este paciente.")

        # ==== Helpers locales (no modifican el resto del archivo) ====
        esc = lambda s: html_escape(str(s if s is not None else ""))

        def _date_es(value: str | None) -> str:
            if not value:
                return "—"
            from datetime import datetime as _dt
            try:
                d = _dt.fromisoformat(value)
            except Exception:
                try:
                    d = _dt.strptime(value, "%Y-%m-%d")
                except Exception:
                    return value
            meses = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
            return f"{d.day:02d} {meses[d.month-1]} {d.year}"

        MODULE_LABELS_ES = {
            "posture": "Postura",
            "cranialNerves": "Nervios craneales",
            "movements": "Movimientos",
            "tone": "Tono",
            "reflexesAndReaction": "Reflejos y reacciones",
        }
        QUESTION_LABELS_ES = {
            # Postura
            "head": "Cabeza", "arms": "Brazos", "feet": "Pies", "hands": "Manos",
            "legs": "Piernas", "trunk": "Tronco",
            # Nervios craneales
            "eyeMovements": "Movimientos oculares", "suckingSwallowing": "Succión/deglución",
            "visualResponse": "Respuesta visual", "facialAppearance": "Apariencia facial",
            "auditoryResponse": "Respuesta auditiva",
            # Movimientos
            "amount": "Cantidad", "quality": "Calidad",
            # Tono
            "pronationPupination": "Pronación/supinación", "pullToSit": "Tracción a sedestación",
            "passiveShoulderElevation": "Elevación pasiva del hombro", "ankleSorsiflexion": "Dorsiflexión del tobillo",
            "poplitealAngle": "Ángulo poplíteo", "scarfSign": "Signo del pañuelo",
            "hipAdductors": "Aductores de cadera", "ventralSuspension": "Suspensión ventral",
            # Reflejos y reacciones
            "armProtection": "Protección de brazos", "parachute": "Paracaídas",
            "tendonReflexes": "Reflejos tendinosos", "lateralSuspension": "Suspensión lateral",
            "verticalSuspension": "Suspensión vertical",
            # Hitos motores
            "LegKicking": "Pataleo", "CephalicControl": "Control cefálico", "Walking": "Marcha",
            "Sitting": "Sedestación", "VoluntaryGrasp": "Prensión voluntaria", "Rolling": "Rodamiento",
            "Crawling": "Gateo", "Standing": "Bipedestación",
            # Comportamiento
            "SocialInteraction": "Interacción social", "EmotionalState": "Estado emocional",
            "StateOfConsciousness": "Estado de conciencia",
        }
        def _label_module(mid: str) -> str:
            return MODULE_LABELS_ES.get(mid, mid)
        def _label_question(qid: str) -> str:
            return QUESTION_LABELS_ES.get(qid, qid)

        COMPANY_TITLE = "El Comite"

        # ==== HTML inline (no requiere plantillas) ====
        from datetime import datetime as _dt
        html_parts = [f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<title>{esc(COMPANY_TITLE)} - Historia clínica HINE - Paciente {esc(child_id)}</title>
<style>
  @page {{ size: A4; margin: 18mm; }}
  body {{ font-family: Arial, Helvetica, sans-serif; font-size: 12px; color: #111; }}
  h1 {{ font-size: 18px; margin: 0 0 6px 0; }}
  h2 {{ font-size: 14px; margin: 12px 0 6px 0; }}
  h3 {{ font-size: 12.5px; margin: 8px 0 4px 0; }}
  table {{ width: 100%; border-collapse: collapse; margin: 6px 0 10px; }}
  th, td {{ border: 1px solid #aaa; padding: 6px; text-align: left; vertical-align: top; }}
  th {{ background: #f3f3f3; }}
</style>
</head>
<body>
  <div style="text-align:center; font-weight:bold; font-size:16px; margin-bottom:6px;">{esc(COMPANY_TITLE)}</div>
  <div style="text-align:center; font-size:11px; color:#555; margin-bottom:10px;">Historia clínica – Hammersmith Infant Neurological Examination</div>
  <h1>Historia clínica HINE</h1>
  <div>Paciente: {esc(child_id)} · Generado: {_dt.now().strftime('%d/%m/%Y %H:%M')}</div>
"""]

        for idx, exam in enumerate(exams):
            data = exam if isinstance(exam, dict) else getattr(exam, "dict", lambda: {})() or getattr(exam, "model_dump", lambda: {})()
            if not isinstance(data, dict):
                raise HTTPException(status_code=500, detail="Formato de examen no soportado (se esperaba dict).")

            if idx > 0:
                html_parts.append('<p style="page-break-before: always;"></p>')

            examId = data.get("examId", "")
            patientId = data.get("patientId", "")
            doctorName = data.get("doctorName", "")
            examDate = _date_es(data.get("examDate"))

            gestationalAge = data.get("gestationalAge", "")
            cronologicalAge = data.get("cronologicalAge", "")
            correctedAge = data.get("correctedAge", "")
            headCircumference = data.get("headCircumference", "")

            analysis = data.get("analysis", {}) or {}
            modules = analysis.get("modules", []) or []
            totalScore = analysis.get("totalScore", "")
            maxPossibleScore = analysis.get("maxPossibleScore", "")
            totalLeftAsymmetries = analysis.get("totalLeftAsymmetries", "")
            totalRightAsymmetries = analysis.get("totalRightAsymmetries", "")

            motor = data.get("motorMilestones", {}) or {}
            motor_resps = motor.get("responses", []) or []

            behavior = data.get("behavior", {}) or {}
            behavior_resps = behavior.get("responses", []) or []

            html_parts.append(f"""
  <h2>Examen #{idx+1}</h2>
  <p><strong>ID Examen:</strong> {esc(examId)} &nbsp;·&nbsp; <strong>Fecha:</strong> {esc(examDate)}</p>
  <p><strong>Médico:</strong> {esc(doctorName)} &nbsp;·&nbsp; <strong>ID Paciente:</strong> {esc(patientId)}</p>
  <p><strong>Edad gestacional (sem):</strong> {esc(gestationalAge)} &nbsp;·&nbsp; <strong>Edad cronológica (mes):</strong> {esc(cronologicalAge)} &nbsp;·&nbsp; <strong>Edad corregida (mes):</strong> {esc(correctedAge)} &nbsp;·&nbsp; <strong>PC (cm):</strong> {esc(headCircumference)}</p>

  <h3>Puntaje global</h3>
  <table>
    <tr><th>Total</th><th>Máximo</th><th>Asim. izq.</th><th>Asim. der.</th></tr>
    <tr>
      <td>{esc(totalScore)}</td>
      <td>{esc(maxPossibleScore)}</td>
      <td>{esc(totalLeftAsymmetries)}</td>
      <td>{esc(totalRightAsymmetries)}</td>
    </tr>
  </table>
""")

            # Módulos
            html_parts.append("<h3>Módulos</h3>")
            for m in modules:
                moduleId = (m or {}).get("moduleId", "")
                obtainedScore = (m or {}).get("obtainedScore", "")
                responses = (m or {}).get("responses", []) or []

                html_parts.append(f"<p><strong>{esc(_label_module(moduleId))}</strong> – Puntaje: {esc(obtainedScore)}</p>")
                html_parts.append("<table><tr><th>Ítem</th><th>Valor</th><th>Izq.</th><th>Der.</th><th>Comentario</th></tr>")

                for r in responses:
                    qid = (r or {}).get("questionId", "")
                    val = (r or {}).get("selectedValue", "")
                    la = (r or {}).get("leftAsymmetry", False)
                    ra = (r or {}).get("rightAsymmetry", False)
                    cmt = (r or {}).get("comment", "") or "—"
                    html_parts.append(
                        f"<tr>"
                        f"<td>{esc(_label_question(qid))}</td>"
                        f"<td>{esc(val)}</td>"
                        f"<td>{'Sí' if la else 'No'}</td>"
                        f"<td>{'Sí' if ra else 'No'}</td>"
                        f"<td>{esc(cmt)}</td>"
                        f"</tr>"
                    )
                html_parts.append("</table>")

            # Hitos motores
            html_parts.append("<h3>Hitos motores</h3><table><tr><th>Hito</th><th>Valor</th><th>Comentario</th></tr>")
            for r in motor_resps:
                qid = (r or {}).get("questionId", "")
                val = (r or {}).get("selectedValue", "")
                cmt = (r or {}).get("comment", "") or "—"
                html_parts.append(f"<tr><td>{esc(_label_question(qid))}</td><td>{esc(val)}</td><td>{esc(cmt)}</td></tr>")
            html_parts.append("</table>")

            # Comportamiento
            html_parts.append("<h3>Comportamiento</h3><table><tr><th>Dimensión</th><th>Valor</th><th>Comentario</th></tr>")
            for r in behavior_resps:
                qid = (r or {}).get("questionId", "")
                val = (r or {}).get("selectedValue", "")
                cmt = (r or {}).get("comment", "") or "—"
                html_parts.append(f"<tr><td>{esc(_label_question(qid))}</td><td>{esc(val)}</td><td>{esc(cmt)}</td></tr>")
            html_parts.append("</table>")

        # Cierre HTML
        html_parts.append("</body></html>")
        html = "\n".join(html_parts)

        # Generar PDF con WeasyPrint (devuelve bytes)
        pdf_bytes = HTML(string=html).write_pdf()
        return pdf_bytes

    def create_exam(self, hine_exam: HineExam) -> HineExam:
        self._validate_required_fields(hine_exam)

        session = None
        try:
            session = Session(engine)

            created_exam = self.exam_service.create_exam(hine_exam)

            # Crear secciones y asignar ítems
            section_ids = {}

            for module in hine_exam.analysis.modules:
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

            self._updateChildrenData(
                hine_exam.patientId,
                hine_exam.gestationalAge,
                hine_exam.cronologicalAge,
                hine_exam.correctedAge,
                hine_exam.headCircumference
            )

            session.commit()

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
        
    def _updateChildrenData(self, child_id: str, gestational_age: str, cronological_age: str, corrected_age: str, head_circumference: str):
        try:
            update_data = ChildUpdate(
                gestational_age=gestational_age,
                cronological_age=cronological_age,
                corrected_age=corrected_age,
                head_circumference=head_circumference
            )
            childService.update_child(child_id, update_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error updating children '{child_id}': {str(e)}"
            )