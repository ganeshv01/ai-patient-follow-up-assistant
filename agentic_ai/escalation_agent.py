
from agentic_ai.state import PatientState
from datetime import date

def escalation_agent(
    state: PatientState,
    reference_date: date | None = None,
) -> PatientState:
    """Evaluate follow-up escalation using explicit workflow metadata."""
    if reference_date is None:
        reference_date = date.today()
    summary = state.get("patient_summary", {})
    contact_history = state.get("contact_history", [])

    severity = str(summary.get("case_severity", "unknown")).lower()
    follow_up_date = summary.get("follow_up_date", "unknown")

    attempts = len(contact_history)
    responses = [
        str(contact.get("status", "")).lower()
        for contact in contact_history
    ]
    patient_responded = any(
        status in {"responded", "replied", "confirmed"}
        for status in responses
    )

    escalate = False
    escalation_severity = severity.upper()
    reason = ""
    recommended_team = []

    # Missing or unsupported metadata requires human review.
    if severity not in {"low", "medium", "high", "unknown"}:
        escalate = True
        escalation_severity = "REVIEW_REQUIRED"
        reason = (
            "Case severity metadata is unsupported. "
            "Human review is required; no risk level will be inferred."
        )
        recommended_team = ["care_team"]

    elif severity == "unknown":
        escalate = True
        escalation_severity = "REVIEW_REQUIRED"
        reason = (
            "Case severity is unknown. Human review is required; "
            "no risk level will be inferred."
        )
        recommended_team = ["care_team"]

    elif not follow_up_date or follow_up_date in {
        "unknown", "Not specified"
    }:
        escalate = True
        escalation_severity = "REVIEW_REQUIRED"
        reason = (
            "Follow-up date is missing from the record. "
            "Human review is required to clarify follow-up timing."
        )
        recommended_team = ["care_team"]

    elif date.fromisoformat(follow_up_date) < reference_date:
        escalate = True
        escalation_severity = "REVIEW_REQUIRED"
        reason = (
            f"Follow-up date {follow_up_date} is overdue relative to "
            f"{reference_date.isoformat()}. Human review is required."
        )
        recommended_team = ["care_team"]

    elif patient_responded:
        reason = (
            "Patient has responded to the follow-up communication. "
            "No contact-attempt escalation is required."
        )

    elif severity == "high":
        # High severity requires review even before failed attempts.
        escalate = True
        escalation_severity = "HIGH"
        reason = (
            "This synthetic case is explicitly labeled high severity "
            "in workflow metadata. Human review is required."
        )
        recommended_team = ["doctor", "nurse", "care_team"]

    elif severity == "medium" and attempts >= 2:
        escalate = True
        escalation_severity = "MEDIUM"
        reason = (
            f"Medium-severity case has no recorded response after "
            f"{attempts} contact attempts."
        )
        recommended_team = ["doctor", "secretary"]

    elif severity == "low" and attempts >= 2:
        escalate = True
        escalation_severity = "LOW"
        reason = (
            f"Case has no recorded response after {attempts} "
            "contact attempts. Human review is required."
        )
        recommended_team = ["secretary"]

    else:
        reason = (
            "Escalation criteria have not been met. "
            f"Attempts: {attempts}; severity metadata: {severity}."
        )

    escalation = {
        "escalate": escalate,
        "severity": escalation_severity,
        "reason": reason,
        "recommended_team": recommended_team,
    }

    return {
        **state,
        "escalation": escalation,
        "status": "escalation_completed",
    }
