
import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from schemas.discharge_summary import DischargeSummary

INPUT = ROOT / "data/sample_records/discharge_summaries.json"
OUTPUT = ROOT / "data/discharge_summaries"


def create_pdf(summary, destination):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="DocumentTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=18,
    ))

    doc = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    story = [
        Paragraph("Discharge Summary", styles["DocumentTitle"]),
        Paragraph(
            "<b>SYNTHETIC TRAINING DOCUMENT — NOT FOR PATIENT CARE</b>",
            styles["BodyText"],
        ),
        Spacer(1, 12),
    ]

    fields = [
        ["Patient ID", summary.patient_id],
        ["Discharge date", str(summary.discharge_date)],
        ["Diagnosis", summary.diagnosis],
        ["Follow-up date", str(summary.follow_up_date or "Not recorded")],
        [
            "Follow-up instructions",
            summary.follow_up_instructions or "Not recorded",
        ],
        ["Required tests status", summary.required_tests_status],
        [
            "Required tests",
            ", ".join(summary.required_tests) or "None listed",
        ],
    ]

    table = Table(fields, colWidths=[1.7 * inch, 4.9 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([table, Spacer(1, 14)])

    story.append(Paragraph("Clinical Notes", styles["Heading2"]))
    story.append(Paragraph(summary.clinical_notes, styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Medications", styles["Heading2"]))
    for medication in summary.medications:
        story.append(Paragraph(
            f"<b>{medication.name}</b>: {medication.instructions}",
            styles["BodyText"],
        ))
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Generated from synthetic structured data for CareLoop software testing.",
        styles["Italic"],
    ))

    doc.build(story)


def main():
    if not INPUT.exists():
        raise SystemExit(f"Input JSON not found: {INPUT}")

    records = json.loads(INPUT.read_text(encoding="utf-8"))
    validated = [DischargeSummary.model_validate(item) for item in records]

    ids = [item.patient_id for item in validated]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate patient IDs found; PDFs were not generated.")

    OUTPUT.mkdir(parents=True, exist_ok=True)

    existing = list(OUTPUT.glob("*.pdf"))
    if existing:
        raise SystemExit(
            f"{len(existing)} PDFs already exist in {OUTPUT}. "
            "Move or review them before regenerating."
        )

    for summary in validated:
        destination = OUTPUT / f"{summary.patient_id}_discharge_summary.pdf"
        create_pdf(summary, destination)

    print(f"Generated {len(validated)} PDFs in {OUTPUT}")


if __name__ == "__main__":
    main()
