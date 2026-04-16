"""
PDF case report generator using ReportLab.
Generates a printable clinical case report.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime


BRAND_COLOR = colors.HexColor("#0F6E56")
EMERGENCY_COLOR = colors.HexColor("#CC2222")
LIGHT_GREEN = colors.HexColor("#E1F5EE")


def generate_case_pdf(case: dict, diagnosis: dict) -> bytes:
    """
    Generate a PDF case report.
    case and diagnosis are dicts (from API response).
    Returns PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", fontSize=18, textColor=BRAND_COLOR,
                                  spaceAfter=4, fontName="Helvetica-Bold", alignment=TA_CENTER)
    subtitle_style = ParagraphStyle("Sub", fontSize=10, textColor=colors.grey,
                                     spaceAfter=12, alignment=TA_CENTER)
    section_style = ParagraphStyle("Section", fontSize=12, textColor=BRAND_COLOR,
                                    fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle("Body", fontSize=10, leading=16, spaceAfter=6)
    emergency_style = ParagraphStyle("Emergency", fontSize=11, textColor=EMERGENCY_COLOR,
                                      fontName="Helvetica-Bold", backColor=colors.HexColor("#FFEEEE"),
                                      borderPad=8)

    story = []

    # Header
    story.append(Paragraph("ClinicalMind", title_style))
    story.append(Paragraph("AI Diagnostic Support Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BRAND_COLOR))
    story.append(Spacer(1, 0.4*cm))

    # Emergency banner
    if diagnosis.get("is_emergency"):
        story.append(Paragraph(
            f"⚠ EMERGENCY: {diagnosis.get('emergency_reason', 'Immediate referral required')}",
            emergency_style
        ))
        story.append(Spacer(1, 0.3*cm))

    # Patient info table
    story.append(Paragraph("Patient Information", section_style))
    patient_data = [
        ["Case ID", str(case.get("id", ""))[:8] + "..."],
        ["Age", str(case.get("patient_age", "Unknown"))],
        ["Sex", case.get("patient_sex", "Unknown")],
        ["Submitted", case.get("created_at", "")[:10]],
        ["Status", case.get("status", "").upper()],
    ]
    patient_table = Table(patient_data, colWidths=[4*cm, 12*cm])
    patient_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GREEN),
        ("TEXTCOLOR", (0, 0), (0, -1), BRAND_COLOR),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.white, colors.HexColor("#F8F8F8")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(patient_table)

    # Symptoms
    story.append(Paragraph("Reported Symptoms", section_style))
    story.append(Paragraph(case.get("symptoms_text", "No symptoms recorded"), body_style))

    # Primary Diagnosis
    story.append(Paragraph("Primary Diagnosis", section_style))
    confidence = diagnosis.get("confidence", 0)
    conf_pct = f"{int(float(confidence) * 100)}%" if confidence else "N/A"
    story.append(Paragraph(
        f"<b>{diagnosis.get('primary_dx', 'Unavailable')}</b> &nbsp;&nbsp; (Confidence: {conf_pct})",
        body_style
    ))

    # Differentials
    differentials = diagnosis.get("differentials", [])
    if differentials:
        story.append(Paragraph("Differential Diagnoses", section_style))
        diff_data = [["Condition", "Confidence", "Reasoning"]]
        for d in differentials:
            diff_data.append([
                d.get("name", ""),
                f"{int(float(d.get('confidence', 0)) * 100)}%",
                d.get("reason", ""),
            ])
        diff_table = Table(diff_data, colWidths=[5*cm, 3*cm, 8.5*cm])
        diff_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREEN]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(diff_table)

    # Treatment Plan
    story.append(Paragraph("Treatment Plan", section_style))
    story.append(Paragraph(diagnosis.get("treatment_plan", "N/A"), body_style))

    # Precautions
    story.append(Paragraph("Precautions & Red Flags", section_style))
    story.append(Paragraph(diagnosis.get("precautions", "N/A"), body_style))

    # When to refer
    story.append(Paragraph("When to Refer", section_style))
    story.append(Paragraph(diagnosis.get("when_to_refer", "N/A"), body_style))

    # References
    refs = diagnosis.get("references", [])
    if refs:
        story.append(Paragraph("Evidence Sources", section_style))
        for r in refs[:5]:
            story.append(Paragraph(f"• {r.get('source', '')} (relevance: {r.get('score', 'N/A')})", body_style))

    # Footer
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Paragraph(
        f"Generated by ClinicalMind AI Diagnostic Support System · {datetime.utcnow().strftime('%d %b %Y %H:%M')} UTC · "
        "This report is a clinical support tool. Not a substitute for professional medical judgment.",
        ParagraphStyle("Footer", fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)
    return buffer.getvalue()
