from agentic_ai.state import PatientState


def reminder_agent(state: PatientState) -> PatientState:
    """
    Creates a structured follow-up reminder from the
    Summary Agent output.

    """

    patient_info = state.get("patient_information", {})
    summary = state.get("patient_summary", {})

    name = patient_info.get("name", "Patient")

    diagnosis = summary.get(
        "diagnosis",
        "your medical condition"
    )

    follow_up_date = summary.get("follow_up_date")

    if not follow_up_date or follow_up_date == "Not specified":
        return {
            **state,
            "reminder": {
                "subject": "Follow-up clarification required",
                "message": (
                    "A follow-up reminder cannot be prepared because "
                    "the discharge summary does not specify a follow-up date. "
                    "Please have the care team review the record."
                ),
                "priority": "review_required",
                "requires_approval": True,
            },
            "status": "awaiting_clarification",
        }

    required_tests = summary.get(
        "required_tests",
        []
    )

    next_steps = summary.get(
        "next_steps",
        []
    )

    important_concerns = summary.get(
        "important_concerns",
        []
    )

    severity = summary.get(
        "case_severity",
        "normal"
    )

    # Determine reminder priority from case severity.
    if severity == "high":
        priority = "high"
    elif severity == "medium":
        priority = "medium"
    else:
        priority = "normal"

    # Build test section.
    if required_tests:
        test_text = (
            "Before your appointment, please complete "
            "the following required tests:\n"
        )

        for test in required_tests:
            test_text += f"- {test}\n"
    else:
        test_text = (
            "No specific tests are currently listed "
            "as required before your appointment.\n"
        )

    # Build next-steps section.
    if next_steps:
        next_steps_text = (
            "\nNext steps:\n"
        )

        for step in next_steps:
            next_steps_text += f"- {step}\n"
    else:
        next_steps_text = ""

    # Explain why tests matter.
    if required_tests:
        test_reason = (
            "\nCompleting these tests before your appointment "
            "will help the care team review your current "
            "condition and prepare for your follow-up.\n"
        )
    else:
        test_reason = ""

    # Add important concerns when relevant.
    if important_concerns:
        concern_text = (
            "\nPlease also follow the instructions provided "
            "by your healthcare team regarding your condition.\n"
        )
    else:
        concern_text = ""

    message = (
        f"Dear {name},\n\n"
        f"This is a reminder about your follow-up appointment "
        f"on {follow_up_date} regarding {diagnosis}.\n\n"
        f"{test_text}"
        f"{test_reason}"
        f"{next_steps_text}"
        f"{concern_text}"
        "\nIf you have questions or are unable to complete "
        "the required steps, please contact your healthcare team.\n\n"
        "Regards,\n"
        "CareLoop Patient Follow-Up Team"
    )

    reminder = {
        "subject": f"Follow-up Reminder - {follow_up_date}",
        "message": message,
        "priority": priority,
        "requires_approval": True,
    }

    return {
        **state,
        "reminder": reminder,
        "status": "reminder_completed",
    }