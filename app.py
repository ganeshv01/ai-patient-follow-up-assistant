import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from run_workflow import load_patient_state
from agentic_ai.workflow import build_workflow


ROOT = Path(__file__).resolve().parent
RECORDS_PATH = ROOT / "data" / "sample_records" / "discharge_summaries.json"

load_dotenv(ROOT / ".env")

st.set_page_config(page_title="CareLoop", page_icon="🏥", layout="wide")
st.title("CareLoop")
st.caption("AI Patient Follow-Up Assistant — synthetic records only")

@st.cache_data
def load_records():
    return json.loads(RECORDS_PATH.read_text(encoding="utf-8"))


records = load_records()
patient_ids = sorted(record["patient_id"] for record in records)

patient_id = st.selectbox("Select synthetic patient", patient_ids)

if st.button("Run follow-up workflow", type="primary"):
    try:
        with st.spinner("Retrieving context and running workflow..."):
            state = load_patient_state(patient_id)
            workflow = build_workflow(require_human_approval=False)
            result = workflow.invoke(state)

        st.session_state["careloop_result"] = result
        st.session_state["careloop_patient_id"] = patient_id

        if result.get("status") == "summary_failed":
            st.error("Summary generation failed. No reminder was generated.")
            for error in result.get("errors", []):
                st.error(error)
        else:
            st.success("Workflow completed. Human approval is pending.")

    except Exception as exc:
        st.error(f"Workflow failed: {exc}")


result = st.session_state.get("careloop_result")
result_patient_id = st.session_state.get("careloop_patient_id")

if result and result_patient_id == patient_id:
    if result.get("status") == "summary_failed":
        st.error("Workflow stopped because summary generation failed.")
        for error in result.get("errors", []):
            st.write(error)
        st.stop()
    
    st.divider()
    st.subheader(f"Patient: {patient_id}")

    summary = result.get("patient_summary", {})
    reminder = result.get("reminder", {})
    escalation = result.get("escalation", {})

    left, right = st.columns(2)

    with left:
        st.markdown("### Patient summary")
        st.write("**Diagnosis:**", summary.get("diagnosis", "Not available"))
        st.write("**Follow-up date:**", summary.get("follow_up_date", "Not specified"))
        st.write("**Case severity metadata:**", summary.get("case_severity", "unknown"))
        st.write("**Previous visit outcome:**", summary.get("previous_visit_outcome", "Not available"))

        st.markdown("**Medications**")
        st.write(summary.get("medications", []))
        st.markdown("**Next steps**")
        st.write(summary.get("next_steps", []))
        st.markdown("**Required tests**")
        st.write(summary.get("required_tests", []))

    with right:
        st.markdown("### Reminder preview")
        st.write("**Subject:**", reminder.get("subject", "Not available"))
        st.write("**Priority:**", reminder.get("priority", "Not available"))
        st.write("**Message:**")
        st.text(reminder.get("message", "No reminder message generated."))

        st.markdown("### Escalation review")
        st.write("**Escalation required:**", escalation.get("escalate", False))
        st.write("**Severity:**", escalation.get("severity", "unknown"))
        st.write("**Reason:**", escalation.get("reason", "No reason provided"))
        st.write("**Recommended team:**", escalation.get("recommended_team", []))

    st.warning("This is a synthetic demo. No patient message will be sent.")

    if result.get("human_decision") in (None, "pending"):
        st.markdown("### Human approval")
        reviewer_comment = st.text_area(
            "Reviewer comment (optional)",
            key=f"comment_{patient_id}",
        )

        approve_col, reject_col = st.columns(2)

        with approve_col:
            if st.button("Approve reminder", type="primary"):
                result["human_decision"] = "approved"
                result["reviewer_comment"] = reviewer_comment
                result["status"] = "approved"
                st.session_state["careloop_result"] = result
                st.rerun()

        with reject_col:
            if st.button("Reject reminder"):
                result["human_decision"] = "rejected"
                result["reviewer_comment"] = reviewer_comment
                result["status"] = "rejected"
                st.session_state["careloop_result"] = result
                st.rerun()

    else:
        st.subheader(f"Decision: {result['human_decision'].upper()}")
        st.write("**Workflow status:**", result.get("status"))
        st.write("**Reviewer comment:**", result.get("reviewer_comment") or "None")
