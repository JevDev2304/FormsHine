# hinereport.py
from fastapi import HTTPException
from html import escape as html_escape
from datetime import datetime as _dt
import pdfkit, shutil, os

class HINEPdfRenderer:
    """
    Renderiza PDFs HINE con un diseño consistente:
    - Logo online en header
    - Footer con © dinámico y paginación
    - Tablas estandarizadas para módulos / hitos / comportamiento
    - wkhtmltopdf con detección multiplataforma

    Debes inyectar los accesos a datos via callables:
      get_exam_by_id(exam_id: str) -> dict|obj
      get_exams_by_child(child_id: str) -> List[dict|obj]
    """
    COMPANY_TITLE = "El Comité"
    LOGO_URL = "https://elcomite.org.co/wp-content/uploads/2023/12/cropped-logo-02.jpg"
    COPYRIGHT_TEXT = "Todos los derechos reservados a sus creadores"

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

    def __init__(self, get_exam_by_id, get_exams_by_child=None,
                 company_title: str | None = None,
                 logo_url: str | None = None,
                 copyright_text: str | None = None):
        self.get_exam_by_id = get_exam_by_id
        self.get_exams_by_child = get_exams_by_child
        if company_title: self.COMPANY_TITLE = company_title
        if logo_url: self.LOGO_URL = logo_url
        if copyright_text: self.COPYRIGHT_TEXT = copyright_text
        self._wkhtml_cfg = self._ensure_wkhtmltopdf()

    # -------------------- API PÚBLICA --------------------

    def render_exam_pdf(self, exam_id: str) -> bytes:
        """PDF de un único examen (por exam_id)."""
        data = self._normalize_exam(self.get_exam_by_id(exam_id))
        html = self._build_document(
            title=f"{self.COMPANY_TITLE} - Historia clínica HINE - Examen {self._esc(data.get('examId', exam_id))}",
            intro_meta="Historia clínica – Hammersmith Infant Neurological Examination",
            sections=[self._exam_section(data, index=1)]
        )
        return self._html_to_pdf(html)

    def render_child_history_pdf(self, child_id: str) -> bytes:
        """PDF con todos los exámenes de un paciente (por child_id)."""
        if not self.get_exams_by_child:
            raise HTTPException(status_code=500, detail="No se configuró get_exams_by_child en HINEPdfRenderer.")
        exams = self.get_exams_by_child(child_id)
        if not exams:
            raise HTTPException(status_code=404, detail="No se encontraron exámenes para este paciente.")

        sections = []
        for idx, exam in enumerate(exams, 1):
            data = self._normalize_exam(exam)
            sections.append(self._exam_section(data, index=idx, page_break=(idx > 1)))

        html = self._build_document(
            title=f"{self.COMPANY_TITLE} - Historia clínica HINE - Paciente {self._esc(child_id)}",
            intro_meta="Historia clínica – Hammersmith Infant Neurological Examination",
            header_extra=f"<div class='small-muted'>Paciente: {self._esc(child_id)} · Generado: {self._now_str()}</div>",
            sections=sections
        )
        return self._html_to_pdf(html)

    def render_exams_batch_pdf(self, exam_ids: list[str]) -> bytes:
        """PDF con varios exámenes, útil para consultas o auditorías."""
        if not exam_ids:
            raise HTTPException(status_code=400, detail="Se requiere al menos un exam_id.")
        sections = []
        for idx, exid in enumerate(exam_ids, 1):
            data = self._normalize_exam(self.get_exam_by_id(exid))
            sections.append(self._exam_section(data, index=idx, page_break=(idx > 1)))
        html = self._build_document(
            title=f"{self.COMPANY_TITLE} - Lote de exámenes HINE ({len(exam_ids)})",
            intro_meta="Historia clínica – Hammersmith Infant Neurological Examination",
            sections=sections
        )
        return self._html_to_pdf(html)

    # -------------------- BLOQUE HTML CORE --------------------

    def _build_document(self, title: str, intro_meta: str, sections: list[str], header_extra: str = "") -> str:
        css = """
        @page { size: A4; margin: 18mm 15mm 20mm 15mm; }  /* espacio para footer */
        body { font-family: Arial, Helvetica, sans-serif; font-size: 12px; color: #111; }
        h1 { font-size: 18px; margin: 0 0 6px 0; }
        h2 { font-size: 14px; margin: 12px 0 6px 0; }
        h3 { font-size: 12.5px; margin: 8px 0 4px 0; }
        table { width: 100%; border-collapse: collapse; margin: 6px 0 10px; }
        th, td { border: 1px solid #aaa; padding: 6px; text-align: left; vertical-align: top; }
        th { background: #f3f3f3; }
        .brand { text-align:center; margin-bottom: 8px; }
        .brand img { height: 120px; }
        .meta { font-size: 11px; color:#555; text-align:center; margin-bottom: 12px; }
        .small-muted { color:#666; font-size: 11px; }
        .page-break { page-break-before: always; }
        """
        parts = [f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<title>{self._esc(title)}</title>
<style>{css}</style>
</head>
<body>
<div class="brand" style="text-align: center;">
  <img src="{self._esc(self.LOGO_URL)}" alt="logo" style="height:200px;"/>
</div>

  <h1>Historia clínica HINE - Hammersmith Infant Neurological Examination</h1>
  <div class="small-muted">Generado: {self._esc(self._now_str())}</div>
  {header_extra}
"""]
        parts.extend(sections)
        parts.append("</body></html>")
        return "\n".join(parts)

    def _exam_section(self, data: dict, index: int, page_break: bool = False) -> str:
        examId = data.get("examId", "")
        patientId = data.get("patientId", "")
        doctorName = data.get("doctorName", "")
        examDate = self._date_es(data.get("examDate"))

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

        parts = []
        if page_break:
            parts.append("<div class='page-break'></div>")

        parts.append(f"""
  <h2>Examen #{index}</h2>
  <p><strong>ID Examen:</strong> {self._esc(examId)} &nbsp;·&nbsp; <strong>Fecha:</strong> {self._esc(examDate)}</p>
  <p><strong>Médico:</strong> {self._esc(doctorName)} &nbsp;·&nbsp; <strong>ID Paciente:</strong> {self._esc(patientId)}</p>
  <p><strong>Edad gestacional (sem):</strong> {self._esc(gestationalAge)} &nbsp;·&nbsp; <strong>Edad cronológica (mes):</strong> {self._esc(cronologicalAge)}
     &nbsp;·&nbsp; <strong>Edad corregida (mes):</strong> {self._esc(correctedAge)} &nbsp;·&nbsp; <strong>PC (cm):</strong> {self._esc(headCircumference)}</p>

  <h3>Puntaje global</h3>
  <table>
    <tr><th>Total</th><th>Máximo</th><th>Asim. izq.</th><th>Asim. der.</th></tr>
    <tr>
      <td>{self._esc(totalScore)}</td>
      <td>{self._esc(maxPossibleScore)}</td>
      <td>{self._esc(totalLeftAsymmetries)}</td>
      <td>{self._esc(totalRightAsymmetries)}</td>
    </tr>
  </table>

  <h3>Módulos</h3>
""")

        # Módulos
        for m in modules:
            moduleId = (m or {}).get("moduleId", "")
            obtainedScore = (m or {}).get("obtainedScore", "")
            responses = (m or {}).get("responses", []) or []

            parts.append(f"<p><strong>{self._esc(self._label_module(moduleId))}</strong> – Puntaje: {self._esc(obtainedScore)}</p>")
            parts.append("<table><tr><th>Ítem</th><th>Valor</th><th>Izq.</th><th>Der.</th><th>Comentario</th></tr>")
            for r in responses:
                qid = (r or {}).get("questionId", "")
                val = (r or {}).get("selectedValue", "")
                la = (r or {}).get("leftAsymmetry", False)
                ra = (r or {}).get("rightAsymmetry", False)
                cmt = (r or {}).get("comment", "") or "—"
                parts.append(
                    f"<tr>"
                    f"<td>{self._esc(self._label_question(qid))}</td>"
                    f"<td>{self._esc(val)}</td>"
                    f"<td>{'Sí' if la else 'No'}</td>"
                    f"<td>{'Sí' if ra else 'No'}</td>"
                    f"<td>{self._esc(cmt)}</td>"
                    f"</tr>"
                )
            parts.append("</table>")

        # Hitos motores
        parts.append("<h3>Hitos motores</h3><table><tr><th>Hito</th><th>Valor</th><th>Comentario</th></tr>")
        for r in motor_resps:
            qid = (r or {}).get("questionId", "")
            val = (r or {}).get("selectedValue", "")
            cmt = (r or {}).get("comment", "") or "—"
            parts.append(f"<tr><td>{self._esc(self._label_question(qid))}</td><td>{self._esc(val)}</td><td>{self._esc(cmt)}</td></tr>")
        parts.append("</table>")

        # Comportamiento
        parts.append("<h3>Comportamiento</h3><table><tr><th>Dimensión</th><th>Valor</th><th>Comentario</th></tr>")
        for r in behavior_resps:
            qid = (r or {}).get("questionId", "")
            val = (r or {}).get("selectedValue", "")
            cmt = (r or {}).get("comment", "") or "—"
            parts.append(f"<tr><td>{self._esc(self._label_question(qid))}</td><td>{self._esc(val)}</td><td>{self._esc(cmt)}</td></tr>")
        parts.append("</table>")

        return "\n".join(parts)

    # -------------------- RENDER PDF --------------------

    def _html_to_pdf(self, html: str) -> bytes:
        year = _dt.now().year
        options = {
            "quiet": "",
            "dpi": "96",
            "page-size": "A4",
            "margin-top": "18mm",
            "margin-right": "15mm",
            "margin-bottom": "18mm",
            "margin-left": "15mm",
            "encoding": "UTF-8",
            "print-media-type": "",
            "load-error-handling": "ignore",
            # Footer
            "footer-center": f"© HINE {year} · {self.COPYRIGHT_TEXT}",
            "footer-right": "Página [page] de [toPage]",
            "footer-font-size": "9",
            "footer-spacing": "3",
        }
        try:
            return pdfkit.from_string(html, False, configuration=self._wkhtml_cfg, options=options)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {e}")

    def _ensure_wkhtmltopdf(self):
        wkhtml_path = shutil.which("wkhtmltopdf")
        if not wkhtml_path:
            for p in [
                r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
                r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
                "/usr/local/bin/wkhtmltopdf",
                "/usr/bin/wkhtmltopdf",
                "/opt/homebrew/bin/wkhtmltopdf",
            ]:
                if os.path.exists(p):
                    wkhtml_path = p
                    break
        if not wkhtml_path:
            raise HTTPException(status_code=500, detail="wkhtmltopdf no encontrado. Instálalo y agrega al PATH o configura la ruta manualmente.")
        return pdfkit.configuration(wkhtmltopdf=wkhtml_path)

    # -------------------- HELPERS REUTILIZABLES --------------------

    @staticmethod
    def _esc(s): return html_escape(str(s if s is not None else ""))

    @staticmethod
    def _now_str(): return _dt.now().strftime('%d/%m/%Y %H:%M')

    @staticmethod
    def _date_es(value: str | None) -> str:
        if not value: return "—"
        try:
            d = _dt.fromisoformat(value)
        except Exception:
            try:
                d = _dt.strptime(value, "%Y-%m-%d")
            except Exception:
                return value
        meses = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
        return f"{d.day:02d} {meses[d.month-1]} {d.year}"

    def _label_module(self, mid: str) -> str:
        return self.MODULE_LABELS_ES.get(mid, mid)

    def _label_question(self, qid: str) -> str:
        return self.QUESTION_LABELS_ES.get(qid, qid)

    @staticmethod
    def _normalize_exam(exam) -> dict:
        if not exam:
            raise HTTPException(status_code=404, detail="No se encontró el examen solicitado.")
        if isinstance(exam, dict): return exam
        data = getattr(exam, "model_dump", lambda: {})() or getattr(exam, "dict", lambda: {})()
        if not isinstance(data, dict):
            raise HTTPException(status_code=500, detail="Formato de examen no soportado (se esperaba dict).")
        return data
