
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from schemas.discharge_summary import DischargeSummary
from scripts.generate_discharge_pdfs import create_pdf

INPUT = ROOT / "data/sample_records/discharge_summaries.json"
OUTPUT = ROOT / "data/discharge_summaries"

def main():
    records = json.loads(INPUT.read_text(encoding="utf-8"))
    summaries = [DischargeSummary.model_validate(item) for item in records]

    ids = [summary.patient_id for summary in summaries]
    if len(summaries) != 200 or len(set(ids)) != 200:
        raise SystemExit(
            f"Expected 200 records with unique IDs; found {len(summaries)} "
            f"records and {len(set(ids))} unique IDs."
        )

    OUTPUT.mkdir(parents=True, exist_ok=True)

    existing_ids = {
        path.stem.removesuffix("_discharge_summary")
        for path in OUTPUT.glob("*.pdf")
    }
    expected_ids = set(ids)

    unexpected = existing_ids - expected_ids
    if unexpected:
        raise SystemExit(f"Unexpected existing PDF IDs; no files generated: {sorted(unexpected)}")

    missing = [summary for summary in summaries if summary.patient_id not in existing_ids]

    for summary in missing:
        destination = OUTPUT / f"{summary.patient_id}_discharge_summary.pdf"
        if destination.exists():
            raise SystemExit(f"Refusing to overwrite existing file: {destination}")
        create_pdf(summary, destination)

    final_ids = {
        path.stem.removesuffix("_discharge_summary")
        for path in OUTPUT.glob("*.pdf")
    }

    if final_ids != expected_ids:
        raise SystemExit(
            f"PDF coverage mismatch. Missing: {sorted(expected_ids - final_ids)}; "
            f"unexpected: {sorted(final_ids - expected_ids)}"
        )

    print(f"Success: generated {len(missing)} new PDFs.")
    print(f"Total PDFs: {len(final_ids)}")
    print("Existing PDFs were preserved.")

if __name__ == "__main__":
    main()
