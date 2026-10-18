from datetime import date

import pytest
from pydantic import ValidationError

from schemas.discharge_summary import DischargeSummary


def valid_record(**overrides):
    record = {
        "patient_id": "P1001",
        "document_type": "discharge_summary",
        "discharge_date": "2026-10-10",
        "diagnosis": "Synthetic example diagnosis",
        "clinical_notes": "Fictional discharge notes for testing.",
        "medications": [
            {
                "name": "Example medication",
                "instructions": "Synthetic example instructions",
            }
        ],
        "required_tests": ["Example follow-up test"],
        "follow_up_date": "2026-10-24",
        "follow_up_instructions": "Contact the care team.",
    }
    record.update(overrides)
    return record


def test_valid_record_passes():
    summary = DischargeSummary.model_validate(valid_record())
    assert summary.patient_id == "P1001"
    assert summary.follow_up_date == date(2026, 10, 24)
    assert summary.needs_follow_up_clarification is False


def test_follow_up_date_must_be_after_discharge():
    with pytest.raises(ValidationError, match="later than"):
        DischargeSummary.model_validate(
            valid_record(follow_up_date="2026-10-10")
        )


def test_follow_up_date_before_discharge_fails():
    with pytest.raises(ValidationError, match="later than"):
        DischargeSummary.model_validate(
            valid_record(follow_up_date="2026-10-08")
        )


def test_missing_follow_up_date_is_allowed_and_flagged():
    summary = DischargeSummary.model_validate(
        valid_record(follow_up_date=None)
    )
    assert summary.follow_up_date is None
    assert summary.needs_follow_up_clarification is True


def test_overdue_follow_up_is_allowed():
    summary = DischargeSummary.model_validate(
        valid_record(follow_up_date="2026-10-15")
    )
    assert summary.follow_up_date < date(2026, 10, 18)


def test_invalid_patient_id_fails():
    with pytest.raises(ValidationError, match="patient_id"):
        DischargeSummary.model_validate(
            valid_record(patient_id="PATIENT-1")
        )


def test_blank_diagnosis_fails():
    with pytest.raises(ValidationError):
        DischargeSummary.model_validate(valid_record(diagnosis="   "))


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError, match="extra"):
        DischargeSummary.model_validate(
            valid_record(unexpected_field="not allowed")
        )
