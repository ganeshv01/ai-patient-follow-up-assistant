from unittest.mock import patch

from agentic_ai.workflow import build_workflow


def test_summary_failure_stops_before_reminder():
    initial_state = {
        "patient_id": "PTEST",
        "patient_information": {},
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

    failed_state = {
        **initial_state,
        "status": "summary_failed",
        "errors": ["Simulated LLM failure"],
    }

    with (
        patch(
            "agentic_ai.workflow.summary_agent",
            return_value=failed_state,
        ),
        patch("agentic_ai.workflow.reminder_agent") as reminder,
    ):
        result = build_workflow(require_human_approval=False).invoke(
            initial_state
        )

    reminder.assert_not_called()
    assert result["status"] == "summary_failed"
    assert result["errors"] == ["Simulated LLM failure"]