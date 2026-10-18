
import json
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError
from schemas.discharge_summary import DischargeSummary

OUTPUT = Path("data/sample_records/discharge_summaries.json")
TODAY = date(2026, 10, 18)



def record(pid, discharged, diagnosis, notes, medications, tests,
           status, follow_up, instructions, case_severity="unknown"):
    return {
        "patient_id": pid,
        "document_type": "discharge_summary",
        "discharge_date": discharged,
        "diagnosis": diagnosis,
        "clinical_notes": notes,
        "medications": [
            {"name": name, "instructions": directions}
            for name, directions in medications
        ],
        "required_tests": tests,
        "required_tests_status": status,
        "follow_up_date": follow_up,
        "follow_up_instructions": instructions,
        "case_severity": case_severity,
    }


records = [
    # Routine follow-up
    record("P1001", "2026-10-10", "Essential hypertension",
           "Blood pressure improved during admission. Discharged in stable condition.",
           [("Amlodipine", "Continue as listed on the discharge medication chart.")],
           ["Blood pressure review"], "specified", "2026-10-24",
           "Arrange a blood pressure review with the treating clinician."),
    record("P1002", "2026-10-12", "Community-acquired pneumonia",
           "Respiratory symptoms improved and oxygen saturation remained stable before discharge.",
           [("Amoxicillin", "Follow the prescribed course recorded on the medication chart.")],
           ["Clinical respiratory assessment"], "specified", "2026-10-22",
           "Review recovery, breathing symptoms and medication tolerance.", case_severity="medium"),
    record("P1003", "2026-10-01", "Type 2 diabetes mellitus",
           "Glucose readings were reviewed during admission. Discharge plan documented.",
           [("Metformin", "Continue according to the discharge medication chart.")],
           ["Fasting blood glucose", "HbA1c as scheduled by the treating team"],
           "specified", "2026-10-15",
           "Review glucose records and the ongoing diabetes management plan.", case_severity="high"),
    record("P1004", "2026-10-14", "Uncomplicated laparoscopic cholecystectomy",
           "Postoperative recovery was uncomplicated. Oral intake and mobility were documented as satisfactory.",
           [("Paracetamol", "Use only as directed on the discharge medication chart.")],
           [], "none_required", "2026-10-28",
           "Review wound healing and recovery at the scheduled surgical appointment."),
    record("P1005", "2026-10-16", "Acute exacerbation of asthma",
           "Wheezing improved following treatment. Inhaler technique was reviewed before discharge.",
           [("Salbutamol inhaler", "Use according to the prescribed inhaler instructions.")],
           ["Respiratory symptom review"], "specified", "2026-10-30",
           "Review symptom control and inhaler use."),
    record("P1006", "2026-10-08", "Iron deficiency anaemia",
           "Laboratory results were consistent with iron deficiency. Outpatient follow-up was documented.",
           [("Ferrous sulfate", "Continue according to the prescribed medication chart.")],
           ["Complete blood count"], "specified", "2026-10-29",
           "Review blood count results and response to treatment."),
    record("P1007", "2026-10-11", "Gastroesophageal reflux disease",
           "Symptoms improved with treatment. The patient was discharged with an outpatient review plan.",
           [("Omeprazole", "Take according to the prescribed medication chart.")],
           ["Symptom and medication review"], "specified", "2026-10-25",
           "Assess symptom control and medication tolerance."),
    record("P1008", "2026-10-13", "Urinary tract infection",
           "Urinary symptoms improved during treatment. Discharge documentation includes a medication plan.",
           [("Nitrofurantoin", "Follow the prescribed course and instructions on the medication chart.")],
           ["Clinical symptom review"], "specified", "2026-10-23",
           "Review symptom resolution and any new concerns."),

    # Follow-up date or instructions missing
    record("P1009", "2026-10-12", "Heart failure",
           "Congestion improved during admission. The discharge record calls for outpatient review, but no date is recorded.",
           [("Furosemide", "Follow the discharge medication chart.")],
           ["Renal function", "Electrolytes"], "specified", None,
           None),
    record("P1010", "2026-10-14", "Chronic obstructive pulmonary disease",
           "Breathing returned to the documented baseline. Outpatient follow-up is mentioned without a confirmed date.",
           [("Tiotropium", "Use according to the prescribed inhaler instructions.")],
           ["Respiratory assessment"], "specified", None,
           "Contact the discharging service to confirm the follow-up appointment."),
    record("P1011", "2026-10-15", "Migraine",
           "Headache symptoms improved before discharge. The source record does not specify a follow-up appointment.",
           [("Sumatriptan", "Use only according to the prescribed medication instructions.")],
           [], "unknown", None, None),
    record("P1012", "2026-10-09", "Chronic kidney disease",
           "Renal function was reviewed during admission. Outpatient monitoring is noted, but the appointment date is absent.",
           [("Amlodipine", "Continue as documented on the discharge medication chart.")],
           ["Renal function", "Electrolytes"], "specified", None,
           "Confirm the timing of laboratory monitoring with the treating service."),
    record("P1013", "2026-10-16", "Cellulitis of the lower limb",
           "Local inflammation improved during admission. Follow-up instructions are incomplete in the source record.",
           [("Cephalexin", "Follow the prescribed course documented on the medication chart.")],
           ["Clinical review of affected area"], "specified", "2026-10-27",
           None),

    # Follow-up dates overdue as of 2026-10-18
    record("P1014", "2026-09-25", "Type 2 diabetes mellitus",
           "Discharged with a plan for review of glucose control and ongoing medication management.",
           [("Metformin", "Continue according to the discharge medication chart.")],
           ["Fasting blood glucose"], "specified", "2026-10-05",
           "Review glucose records and the treatment plan."),
    record("P1015", "2026-09-28", "Essential hypertension",
           "Blood pressure management was reviewed. Outpatient monitoring was requested.",
           [("Amlodipine", "Continue according to the prescribed medication chart.")],
           ["Blood pressure review"], "specified", "2026-10-08",
           "Review blood pressure readings and medication tolerance."),
    record("P1016", "2026-10-02", "Community-acquired pneumonia",
           "Symptoms improved and discharge was completed with a respiratory follow-up plan.",
           [("Amoxicillin", "Follow the prescribed course recorded on the medication chart.")],
           ["Respiratory assessment"], "specified", "2026-10-12",
           "Assess recovery and any persistent respiratory symptoms."),
    record("P1017", "2026-09-30", "Iron deficiency anaemia",
           "Discharge plan includes monitoring of anaemia and review of laboratory results.",
           [("Ferrous sulfate", "Continue according to the prescribed medication chart.")],
           ["Complete blood count"], "specified", "2026-10-10",
           "Review laboratory results and ongoing management."),
    record("P1018", "2026-10-04", "Heart failure",
           "Clinical status improved during admission. Follow-up and laboratory monitoring were requested.",
           [("Furosemide", "Follow the discharge medication chart.")],
           ["Renal function", "Electrolytes"], "specified", "2026-10-14",
           "Review symptoms, laboratory results and the documented management plan."),

    # Additional conditions and monitoring needs
    record("P1019", "2026-10-06", "Atrial fibrillation",
           "Heart rhythm and rate were assessed during admission. The discharge record includes an outpatient review plan.",
           [("Apixaban", "Follow the prescribed medication chart and documented precautions.")],
           ["Cardiology review"], "specified", "2026-10-27",
           "Review rhythm management and medication tolerance."),
    record("P1020", "2026-10-07", "Community-acquired pneumonia",
           "Clinical improvement was documented. The patient was discharged with a plan for symptom reassessment.",
           [("Amoxicillin", "Follow the prescribed course recorded on the medication chart.")],
           ["Respiratory symptom review"], "specified", "2026-10-20",
           "Assess recovery and confirm whether symptoms have resolved."),
    record("P1021", "2026-10-10", "Postoperative recovery following hernia repair",
           "Recovery was documented as stable. Wound care and outpatient review were included in the discharge plan.",
           [("Paracetamol", "Use only as directed on the discharge medication chart.")],
           [], "none_required", "2026-10-24",
           "Review wound healing and postoperative recovery."),
    record("P1022", "2026-10-11", "Hypothyroidism",
           "Thyroid replacement therapy was documented. Outpatient review is required to assess ongoing management.",
           [("Levothyroxine", "Take according to the prescribed medication chart.")],
           ["Thyroid function tests"], "specified", "2026-11-08",
           "Review thyroid function results and the ongoing treatment plan."),
    record("P1023", "2026-10-12", "Acute kidney injury",
           "Renal function improved during admission. Repeat laboratory monitoring is included in the discharge plan.",
           [("Amlodipine", "Continue only as listed on the discharge medication chart.")],
           ["Renal function", "Electrolytes"], "specified", "2026-10-20",
           "Review laboratory results promptly and follow the documented care plan."),
    record("P1024", "2026-10-13", "Type 2 diabetes mellitus with hyperglycaemia",
           "Glucose management was reviewed during admission. The discharge record requests early outpatient reassessment.",
           [("Metformin", "Follow the prescribed medication chart.")],
           ["Fasting blood glucose"], "specified", "2026-10-21",
           "Review glucose readings and the documented diabetes management plan."),
    record("P1025", "2026-10-15", "Asthma",
           "Symptoms improved before discharge. The record notes a need to confirm the outpatient review arrangements.",
           [("Salbutamol inhaler", "Use according to the prescribed inhaler instructions.")],
           ["Respiratory symptom review"], "specified", "2026-10-22",
           "Confirm the appointment and review symptom control."),
]


def main():
    if len(records) != 25:
        raise SystemExit(f"Expected 25 records, found {len(records)}")

    validated = []
    ids = set()

    for item in records:
        try:
            summary = DischargeSummary.model_validate(item)
        except ValidationError as exc:
            print(f"\nINVALID RECORD: {item['patient_id']}\n{exc}")
            raise SystemExit("Dataset not saved. Fix validation errors first.")

        if summary.patient_id in ids:
            raise SystemExit(f"Duplicate patient ID: {summary.patient_id}")

        ids.add(summary.patient_id)
        validated.append(summary.model_dump(mode="json"))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if OUTPUT.exists():
        backup = OUTPUT.with_suffix(".json.bak")
        shutil.copy2(OUTPUT, backup)
        print(f"Previous dataset backed up to: {backup}")

    OUTPUT.write_text(json.dumps(validated, indent=2) + "\n", encoding="utf-8")

    print(f"\nSUCCESS: saved {len(validated)} validated records to {OUTPUT}")
    print(f"Unique patient IDs: {len(ids)}")
    print(f"Overdue follow-ups: {sum(
        item.follow_up_date is not None and item.follow_up_date < TODAY
        for item in map(DischargeSummary.model_validate, validated)
    )}")
    print(f"Missing follow-up dates: {sum(item['follow_up_date'] is None for item in validated)}")


if __name__ == "__main__":
    main()
