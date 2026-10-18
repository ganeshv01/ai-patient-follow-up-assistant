from langgraph.graph import StateGraph, START, END

from agentic_ai.state import PatientState
from agentic_ai.summary_agent import summary_agent
from agentic_ai.reminder_agent import reminder_agent
from agentic_ai.escalation_agent import escalation_agent


def human_approval(state: PatientState) -> PatientState:
    """Terminal-based human approval."""
    reminder = state.get("reminder", {})
    escalation = state.get("escalation", {})

    print("\n" + "=" * 60)
    print("HUMAN APPROVAL REQUIRED")
    print("=" * 60)
    print("\nReminder Subject:", reminder.get("subject"))
    print("\nReminder Message:", reminder.get("message"))
    print("\nPriority:", reminder.get("priority"))

    if escalation.get("escalate"):
        print("\nEscalation:", escalation.get("reason"))
        print("Recommended team:", escalation.get("recommended_team"))

    decision = input("\nEnter [a]pprove or [r]eject: ").strip().lower()

    if decision == "a":
        return {
            **state,
            "human_decision": "approved",
            "status": "approved",
        }
    if decision == "r":
        return {
            **state,
            "human_decision": "rejected",
            "status": "rejected",
        }

    return {
        **state,
        "human_decision": "pending",
        "status": "awaiting_approval",
    }


def route_after_escalation(state: PatientState) -> str:
    if state.get("escalation", {}).get("escalate") is True:
        return "escalation_review"
    return "approval_step"


def escalation_review(state: PatientState) -> PatientState:
    escalation = state.get("escalation", {})
    print("\n--- ESCALATION REVIEW ---")
    print("Severity:", escalation.get("severity"))
    print("Reason:", escalation.get("reason"))
    print("Recommended team:", escalation.get("recommended_team"))

    return {
        **state,
        "status": "escalation_pending_review",
    }


def approval_pending(state: PatientState) -> PatientState:
    """Leave the reminder awaiting a decision from the UI."""
    return {
        **state,
        "human_decision": "pending",
        "status": "awaiting_approval",
    }

def route_after_summary(state: PatientState) -> str:
    """Do not generate reminders if summary generation failed."""
    if state.get("status") == "summary_failed":
        return "stop"
    return "continue"

def build_workflow(require_human_approval: bool = True):
    """Build the workflow for terminal or browser use."""
    graph = StateGraph(PatientState)

    graph.add_node("summary_agent", summary_agent)
    graph.add_node("reminder_agent", reminder_agent)
    graph.add_node("escalation_agent", escalation_agent)
    graph.add_node("escalation_review", escalation_review)

    if require_human_approval:
        graph.add_node("approval_step", human_approval)
    else:
        graph.add_node("approval_step", approval_pending)

    graph.add_edge(START, "summary_agent")
    graph.add_conditional_edges(
        "summary_agent",
        route_after_summary,
        {
            "continue": "reminder_agent",
            "stop": END,
        },
    )
    graph.add_edge("reminder_agent", "escalation_agent")

    graph.add_conditional_edges(
        "escalation_agent",
        route_after_escalation,
        {
            "escalation_review": "escalation_review",
            "approval_step": "approval_step",
        },
    )

    graph.add_edge("escalation_review", "approval_step")
    graph.add_edge("approval_step", END)

    return graph.compile()