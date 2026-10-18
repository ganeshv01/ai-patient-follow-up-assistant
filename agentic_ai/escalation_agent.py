from agentic_ai.state import PatientState


def escalation_agent(state: PatientState) -> PatientState:
    """
    Evaluates whether a patient requires escalation.

    Decision is based on:
    - case severity
    - follow-up status
    - number of contact attempts
    - response status
    """

    summary = state.get("patient_summary", {})
    contact_history = state.get("contact_history", [])

    severity = summary.get(
        "case_severity",
        "normal"
    ).lower()

    follow_up_date = summary.get(
        "follow_up_date",
        "unknown"
    )

    # Count contact attempts.
    attempts = len(contact_history)

    # Determine whether the patient has responded.
    responses = [
        contact.get("status", "").lower()
        for contact in contact_history
    ]

    patient_responded = any(
        status in ["responded", "replied", "confirmed"]
        for status in responses
    )

    # Default decision.
    escalate = False
    escalation_severity = severity.upper()
    reason = ""
    recommended_team = []

    # Missing or uncertain source data requires human review.
    if severity not in {"high", "medium", "normal"}:
        escalate = True
        escalation_severity = "REVIEW_REQUIRED"
        reason = (
            "Case severity is unknown or unsupported. "
            "Human review is required; no risk level will be inferred."
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

    # --------------------------------
    # Patient has responded
    # --------------------------------

    elif patient_responded:

        reason = (
            "Patient has responded to the follow-up "
            "communication. No escalation is required."
        )

    # --------------------------------
    # High-risk patient
    # --------------------------------

    elif severity == "high" and attempts >= 1:

        escalate = True
        escalation_severity = "HIGH"

        reason = (
            f"High-risk patient has not responded after "
            f"{attempts} contact attempt(s). Follow-up date: "
            f"{follow_up_date}."
        )

        recommended_team = [
            "doctor",
            "nurse",
            "secretary",
        ]

    # --------------------------------
    # Medium-risk patient
    # --------------------------------

    elif severity == "medium" and attempts >= 2:

        escalate = True
        escalation_severity = "MEDIUM"

        reason = (
            f"Medium-risk patient has not responded after "
            f"{attempts} contact attempts."
        )

        recommended_team = [
            "doctor",
            "secretary",
        ]

    # --------------------------------
    # Normal-risk patient
    # --------------------------------

    elif severity == "normal" and attempts >= 2:

        escalate = True
        escalation_severity = "NORMAL"

        reason = (
            f"Patient has not responded after "
            f"{attempts} contact attempts."
        )

        recommended_team = [
            "secretary",
        ]

    # --------------------------------
    # No escalation yet
    # --------------------------------

    else:

        reason = (
            f"Patient has not responded, but escalation "
            f"criteria have not yet been met. "
            f"Attempts: {attempts}, risk: {severity}."
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