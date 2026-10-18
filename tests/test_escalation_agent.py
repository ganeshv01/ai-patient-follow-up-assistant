from agentic_ai.escalation_agent import escalation_agent
from datetime import date

def make_state(
    severity="medium",
    follow_up_date="2026-10-22",
    contact_history=None,
):
    return {
        "patient_id": "PTEST",
        "patient_information": {},
        "patient_summary": {
            "case_severity": severity,
            "follow_up_date": follow_up_date,
        },
        "reminder": {},
        "retrieved_context": [],
        "contact_history": contact_history or [],
        "escalation": {},
        "human_decision": None,
        "reviewer_comment": None,
        "status": "started",
        "errors": [],
    }


def test_high_severity_requires_review():
    result = escalation_agent(make_state(severity="high"))
    assert result["escalation"]["escalate"] is True
    assert result["escalation"]["severity"] == "HIGH"


def test_medium_without_attempts_does_not_escalate():
    result = escalation_agent(make_state(severity="medium"))
    assert result["escalation"]["escalate"] is False


def test_unknown_severity_requires_review():
    result = escalation_agent(make_state(severity="unknown"))
    assert result["escalation"]["escalate"] is True
    assert result["escalation"]["severity"] == "REVIEW_REQUIRED"


def test_missing_follow_up_date_requires_review():
    result = escalation_agent(
        make_state(severity="medium", follow_up_date="Not specified")
    )
    assert result["escalation"]["escalate"] is True
    assert result["escalation"]["severity"] == "REVIEW_REQUIRED"


def test_patient_response_avoids_contact_attempt_escalation():
    history = [{"status": "responded"}, {"status": "responded"}]
    result = escalation_agent(
        make_state(severity="medium", contact_history=history)
    )
    assert result["escalation"]["escalate"] is False

def test_overdue_follow_up_requires_review():
    result = escalation_agent(
        make_state(
            severity="medium",
            follow_up_date="2026-10-15",
        ),
        reference_date=date(2026, 10, 18),
    )

    assert result["escalation"]["escalate"] is True
    assert result["escalation"]["severity"] == "REVIEW_REQUIRED"
    assert "overdue" in result["escalation"]["reason"].lower()