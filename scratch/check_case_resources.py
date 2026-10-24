import json, csv, os
from pathlib import Path

# Load all files
DATASET_DIR = Path("dataset")
samples = list(csv.DictReader(open(DATASET_DIR / "sample_deletion_requests.csv", encoding="utf-8")))
sample_out = {r['case_id']: r for r in csv.DictReader(open(DATASET_DIR / "sample_output.csv", encoding="utf-8"))}
ev_files = list(csv.DictReader(open(DATASET_DIR / "evidence_files.csv", encoding="utf-8")))
ev_by_id = {r['file_id']: r for r in ev_files}

print("Checking where sample case resources appear across evidence files:")
for s in samples[:10]:
    cid = s['case_id']
    steps = json.loads(sample_out[cid]['steps_json'])
    resources = set(step['resource_id'] for step in steps)
    expected_evs = set(step['evidence_id'] for step in steps if step['evidence_id'])
    print(f"\n{cid} (audit_at {s['audit_at']}): resources={resources}, expected_evs={expected_evs}")
