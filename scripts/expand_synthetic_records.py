
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from schemas.discharge_summary import DischargeSummary

OUTPUT = ROOT / "data/sample_records/discharge_summaries.json"
TODAY = date(2026, 10, 18)
TARGET_COUNT = 200

# Synthetic templates for software testing only; not clinical guidance.
TEMPLATES = [
    {
        "diagnosis": "Essential hypertension",
        "notes": "Synthetic record: blood pressure management was reviewed during admission.",
        "medications": [("Amlodipine", "Follow the instructions on the discharge medication chart.")],
        "tests": ["Blood pressure review"],
        "instructions": "Arrange the planned review with the treating clinician.",
    },
    {
        "diagnosis": "Community-acquired pneumonia",
        "notes": "Synthetic record: respiratory symptoms improved before discharge.",
        "medications": [("Amoxicillin", "Follow the prescribed course documented on the medication chart.")],
        "tests": ["Respiratory symptom review"],
        "instructions": "Review recovery and medication tolerance with the treating team.",
    },
    {
        "diagnosis": "Type 2 diabetes mellitus",
        "notes": "Synthetic record: glucose readings were reviewed and outpatient monitoring was documented.",
        "medications": [("Metformin", "Follow the instructions on the discharge medication chart.")],
        "tests": ["Fasting blood glucose"],
        "instructions": "Review glucose records and the documented management plan.",
    },
    {
        "diagnosis": "Asthma",
        "notes": "Synthetic record: symptoms improved and inhaler instructions were documented.",
        "medications": [("Salbutamol inhaler", "Use according to the prescribed inhaler instructions.")],
        "tests": ["Respiratory symptom review"],
        "instructions": "Review symptom control with the treating clinician.",
    },
    {
        "diagnosis": "Iron deficiency anaemia",
        "notes": "Synthetic record: outpatient monitoring of anaemia was included in the discharge plan.",
        "medications": [("Ferrous sulfate", "Follow the instructions on the discharge medication chart.")],
        "tests": ["Complete blood count"],
        "instructions": "Review the planned laboratory results with the treating team.",
    },
    {
        "diagnosis": "Heart failure",
        "notes": "Synthetic record: the discharge plan documented outpatient review and monitoring.",
        "medications": [("Furosemide", "Follow the discharge medication chart.")],
        "tests": ["Renal function", "Electrolytes"],
        "instructions": "Arrange the documented follow-up and laboratory review.",
    },
    {
        "diagnosis": "Chronic kidney disease",
        "notes": "Synthetic record: renal monitoring was documented in the discharge plan.",
        "medications": [("Amlodipine", "Follow the instructions on the discharge medication chart.")],
        "tests": ["Renal function", "Electrolytes"],
        "instructions": "Confirm the timing of monitoring with the treating service.",
    },
    {
        "diagnosis": "Gastroesophageal reflux disease",
        "notes": "Synthetic record: symptoms improved and an outpatient review plan was recorded.",
        "medications": [("Omeprazole", "Follow the instructions on the discharge medication chart.")],
        "tests": ["Symptom and medication review"],
        "instructions": "Review symptom control and medication tolerance.",
    },
    {
        "diagnosis": "Urinary tract infection",
        "notes": "Synthetic record: urinary symptoms improved during treatment.",
        "medications": [("Nitrofurantoin", "Follow the prescribed course and medication chart.")],
        "tests": ["Clinical symptom review"],
        "instructions": "Review symptom resolution with the treating clinician.",
    },
    {
        "diagnosis": "Hypothyroidism",
        "notes": "Synthetic record: thyroid replacement therapy and outpatient review were documented.",
        "medications": [("Levothyroxine", "Follow the instructions on the discharge medication chart.")],
        "tests": ["Thyroid function tests"],
        "instructions": "Review the planned thyroid function results with the treating team.",
    },
]

def build_record(number: int) -> dict:
    template = TEMPLATES[(number - 1026) % len(TEMPLATES)]

    # Cycle through upcoming, overdue, and missing-date follow-up scenarios.
    scenario = (number - 1026) % 10
    discharge = TODAY - timedelta(days=3 + ((number * 7) % 35))

    if scenario in (0, 1):
        follow_up = None
        instructions = (
            "Contact the discharging service to confirm the follow-up appointment."
        )
    elif scenario in (2, 3, 4):
        follow_up = discharge + timedelta(days=3 + (number % 8))
        instructions = template["instructions"]
    else:
        follow_up = TODAY + timedelta(days=2 + (number % 21))
        instructions = template["instructions"]

    # Synthetic workflow metadata only; not a clinical risk assessment.
    severity = ("low", "medium", "high", "unknown")[number % 4]

    return {
        "patient_id": f"P{number}",
        "document_type": "discharge_summary",
        "discharge_date": discharge.isoformat(),
        "diagnosis": template["diagnosis"],
        "clinical_notes": template["notes"],
        "medications": [
            {"name": name, "instructions": directions}
            for name, directions in template["medications"]
        ],
        "required_tests": template["tests"],
        "required_tests_status": "specified",
        "follow_up_date": follow_up.isoformat() if follow_up else None,
        "follow_up_instructions": instructions,
        "case_severity": severity,
    }

def main():
    if not OUTPUT.exists():
        raise SystemExit(f"Existing dataset not found: {OUTPUT}")

    existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
    existing_ids = [item["patient_id"] for item in existing]

    if len(existing) != 25 or len(set(existing_ids)) != 25:
        raise SystemExit(
            f"Expected 25 existing records with unique IDs; found {len(existing)} "
            f"records and {len(set(existing_ids))} unique IDs. No changes made."
        )

    if any(item["patient_id"] != f"P{1001 + i}" for i, item in enumerate(existing)):
        raise SystemExit("Existing IDs are not P1001-P1025 in order. No changes made.")

    additions = [build_record(number) for number in range(1026, 1201)]
    combined = existing + additions

    validated = []
    seen = set()

    try:
        for item in combined:
            record = DischargeSummary.model_validate(item)
            if record.patient_id in seen:
                raise ValueError(f"Duplicate patient ID: {record.patient_id}")
            seen.add(record.patient_id)
            validated.append(record.model_dump(mode="json"))
    except (ValidationError, ValueError) as exc:
        raise SystemExit(f"Validation failed; original JSON unchanged:\n{exc}")

    backup = OUTPUT.with_suffix(".json.before_200.bak")
    if backup.exists():
        raise SystemExit(
            f"Safety stop: backup already exists at {backup}. "
            "Review it before running again."
        )

    backup.write_text(OUTPUT.read_text(encoding="utf-8"), encoding="utf-8")
    OUTPUT.write_text(
        json.dumps(validated, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Success: {len(validated)} validated records saved.")
    print(f"IDs: {validated[0]['patient_id']} through {validated[-1]['patient_id']}")
    print(f"Original dataset backed up to: {backup}")
    print("No PDFs or ChromaDB entries were changed.")

if __name__ == "__main__":
    main()
