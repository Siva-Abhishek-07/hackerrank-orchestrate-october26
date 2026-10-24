import json, csv
from datetime import datetime, timedelta
from pathlib import Path

DATASET_DIR = Path("dataset")
samples = list(csv.DictReader(open(DATASET_DIR / "sample_deletion_requests.csv", encoding="utf-8")))
sample_out = {r['case_id']: r for r in csv.DictReader(open(DATASET_DIR / "sample_output.csv", encoding="utf-8"))}
activities = list(csv.DictReader(open(DATASET_DIR / "system_activity.csv", encoding="utf-8")))

for a in activities:
    a['dt'] = datetime.fromisoformat(a['event_time'].replace('Z', '+00:00'))

for s in samples[:10]:
    cid = s['case_id']
    req_dt = datetime.fromisoformat(s['requested_at'].replace('Z', '+00:00'))
    rep_dt = datetime.fromisoformat(s['reported_at'].replace('Z', '+00:00'))
    gold_steps = json.loads(sample_out[cid]['steps_json'])
    gold_res = [st['resource_id'] for st in gold_steps]
    
    # Check deletion worker activities on account_service within [req_dt, rep_dt + 1 hour]
    acts = [a for a in activities if a['source_system'] == 'deletion_worker' and a['target_system'] == 'account_service' and req_dt - timedelta(hours=1) <= a['dt'] <= rep_dt + timedelta(hours=2)]
    print(f"\n{cid} (rep: {s['reported_at']}): gold_res = {gold_res}")
    for a in acts:
        diff_mins = (a['dt'] - rep_dt).total_seconds() / 60
        print(f"  {a['resource_id']} | {a['event_type']} | {a['reported_result']} | diff={diff_mins:+.1f} min")
