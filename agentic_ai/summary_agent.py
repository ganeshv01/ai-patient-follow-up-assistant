from agentic_ai.state import PatientState


def summary_agent(state: PatientState) -> PatientState:
    """
    Creates a structured patient follow-up summary.

    Currently uses deterministic logic so the workflow can be developed.

    Later, this function will use the LLM with RAG context.
    """

    patient_info = state.get("patient_information", {})
    retrieved_context = state.get("retrieved_context", [])

    diagnosis = patient_info.get(
        "diagnosis",
        "Not specified"
    )

    follow_up_date = patient_info.get("follow_up_date")
    if not follow_up_date:
        follow_up_date = "Not specified"
    previous_visit_outcome = patient_info.get(
        "previous_visit_outcome",
        "Not specified"
    )

    medications = patient_info.get(
        "medications",
        []
    )

    next_steps = patient_info.get(
        "next_steps",
        []
    )

    required_tests = patient_info.get(
        "required_tests",
        []
    )

    important_concerns = patient_info.get(
        "important_concerns",
        []
    )

    case_severity = patient_info.get(
        "case_severity",
        "normal"
    )

    # Use retrieved RAG context when available.
    # The real LLM-based implementation will interpret
    # this context rather than simply copying it.
    if retrieved_context:
        previous_visit_outcome = (
            previous_visit_outcome
            if previous_visit_outcome != "Not specified"
            else retrieved_context[0]
        )

    summary = {
        "diagnosis": diagnosis,
        "previous_visit_outcome": previous_visit_outcome,
        "medications": medications,
        "next_steps": next_steps,
        "required_tests": required_tests,
        "follow_up_date": follow_up_date,
        "important_concerns": important_concerns,
        "case_severity": case_severity,
    }

    return {
        **state,
        "patient_summary": summary,
        "status": "summary_completed",
    }