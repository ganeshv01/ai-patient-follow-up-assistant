# CareLoop Follow-Up Policy

## 1. Purpose

This policy defines the rules used by CareLoop to identify follow-up needs, prepare reminders, and flag cases for human review. All records used for this capstone are synthetic.

## 2. Follow-Up Status

- **Upcoming:** The follow-up date is in the future.
- **Due today:** The follow-up date is today.
- **Overdue:** The follow-up date is before today.
- **Date missing:** No follow-up date is recorded. Do not invent one; flag the case for clarification.
- **Instructions missing:** Follow-up instructions are absent. Flag the missing information for review.

## 3. Reminder Handling

- Prepare a reminder when a valid follow-up date and sufficient instructions are available.
- Include only information supported by the discharge record.
- Do not invent appointments, test results, medication changes, or clinical advice.
- Require human approval before any reminder is considered sent.

## 4. Escalation Rules

- Flag overdue follow-ups for review.
- Track reminder attempts and their outcomes in contact history.
- Flag repeated unsuccessful contact attempts for human review.
- Escalate cases with missing or conflicting information rather than guessing.
- Do not automatically mark a patient as contacted when no successful contact is recorded.

## 5. Human Approval

- A proposed reminder or escalation must be reviewed before an external action is taken.
- Record whether the proposal was approved or rejected.
- Record the final workflow status and the reason for the decision.
- This capstone does not send real patient communications.

## 6. Data and Safety

- Use synthetic patient records only.
- Treat discharge summaries as the source of patient-specific information.
- Treat this policy as workflow logic for software testing, not a clinical guideline.
- When information is insufficient, request clarification or human review.
