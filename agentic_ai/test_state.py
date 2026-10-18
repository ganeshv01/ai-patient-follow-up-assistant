
from agentic_ai.state import PatientState


def test_patient_state_has_required_fields():
    patient_state: PatientState = {
        "patient_id": "P1002",
        "patient_information": {
            "diagnosis": "Community-acquired pneumonia",
            "previous_visit_outcome": (
                "Respiratory symptoms improved and oxygen saturation "
                "remained stable before discharge."
            ),
            "medications": [
                "Amoxicillin: Follow the prescribed course recorded "
                "on the medication chart."
            ],
            "next_steps": [
                "Review recovery, breathing symptoms and medication tolerance."
            ],
            "required_tests": ["Clinical respiratory assessment"],
            "follow_up_date": "2026-10-22",
            "important_concerns": [],
            "case_severity": "unknown",
        },
        "retrieved_context": [],
        "patient_summary": {},
        "reminder": {},
        "contact_history": [],
        "escalation": {},
        "human_decision": None,
        "reviewer_comment": None,
        "status": "started",
        "errors": [],
    }

    assert patient_state["patient_id"] == "P1002"
    assert patient_state["status"] == "started"
    assert isinstance(patient_state["patient_information"], dict)
    assert isinstance(patient_state["patient_summary"], dict)
    assert isinstance(patient_state["reminder"], dict)
