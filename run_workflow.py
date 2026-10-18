import os
from pathlib import Path
import json
from schemas.discharge_summary import DischargeSummary
import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from agentic_ai.state import PatientState
from agentic_ai.workflow import build_workflow

def retrieve_patient_context(patient_id: str) -> list[str]:
    """Retrieve only the discharge-summary chunks for one patient."""
    load_dotenv(Path(__file__).resolve().parent / ".env")

    embeddings = OpenAIEmbeddings(
        model=os.getenv(
            "OPENAI_EMBEDDING_MODEL",
            "text-embedding-3-small",
        )
    )

    client = chromadb.HttpClient(host="localhost", port=8000)

    store = Chroma(
        client=client,
        collection_name="careloop_discharge_summaries",
        embedding_function=embeddings,
    )

    results = store.similarity_search(
        "discharge diagnosis, follow-up date, instructions, "
        "required tests, clinical notes, and medications",
        k=5,
        filter={"patient_id": patient_id},
    )

    return [doc.page_content for doc in results]

def print_node_update(node_name: str, state: PatientState):
    print("\n" + "=" * 60)
    print(f"NODE COMPLETED: {node_name}")
    print("=" * 60)

    print("Status:", state.get("status"))

    if node_name == "summary_agent":
        print("\nPatient Summary:")
        for key, value in state.get("patient_summary", {}).items():
            print(f"  {key}: {value}")

    elif node_name == "reminder_agent":
        reminder = state.get("reminder", {})
        print("\nReminder:")
        print("  Subject:", reminder.get("subject"))
        print("  Priority:", reminder.get("priority"))
        print(
            "  Requires approval:",
            reminder.get("requires_approval")
        )

    elif node_name == "escalation_agent":
        print("\nEscalation:")
        for key, value in state.get("escalation", {}).items():
            print(f"  {key}: {value}")

    elif node_name == "human_approval":
        print("\nHuman Decision:")
        print(" ", state.get("human_decision"))


def load_patient_state(patient_id: str) -> PatientState:
    """Build workflow state from a validated synthetic discharge record."""
    records_path = (
        Path(__file__).resolve().parent
        / "data"
        / "sample_records"
        / "discharge_summaries.json"
    )

    records = json.loads(records_path.read_text(encoding="utf-8"))
    matching_records = [
        record for record in records
        if record.get("patient_id") == patient_id
    ]

    if len(matching_records) != 1:
        raise ValueError(
            f"Expected exactly one record for {patient_id}; "
            f"found {len(matching_records)}."
        )

    summary = DischargeSummary.model_validate(matching_records[0])
    retrieved_context = retrieve_patient_context(patient_id)

    if not retrieved_context:
        raise RuntimeError(
            f"No ChromaDB context found for patient {patient_id}."
        )

    return {
        "patient_id": summary.patient_id,
        "patient_information": {
            "diagnosis": summary.diagnosis,
            "previous_visit_outcome": summary.clinical_notes,
            "medications": [
                f"{med.name}: {med.instructions}"
                for med in summary.medications
            ],
            "next_steps": (
                [summary.follow_up_instructions]
                if summary.follow_up_instructions
                else []
            ),
            "required_tests": summary.required_tests,
            "follow_up_date": (
                summary.follow_up_date.isoformat()
                if summary.follow_up_date
                else "Not specified"
            ),
            "important_concerns": [],
            "case_severity": summary.case_severity,
        },
        "retrieved_context": retrieved_context,
        "patient_summary": {},
        "reminder": {},
        "contact_history": [],
        "escalation": {},
        "human_decision": None,
        "reviewer_comment": None,
        "status": "started",
        "errors": [],
    }


patient_state = load_patient_state("P1002")


workflow = build_workflow()

print("\n" + "=" * 60)
print("CARELOOP AGENTIC WORKFLOW")
print("=" * 60)

print("\nInitial patient:", patient_state["patient_id"])
print("Starting workflow...")


# Stream the graph so we can see every node as it completes.
for event in workflow.stream(patient_state):

    for node_name, state_update in event.items():

        print_node_update(
            node_name,
            state_update
        )


print("\n" + "=" * 60)
print("WORKFLOW COMPLETE")
print("=" * 60)