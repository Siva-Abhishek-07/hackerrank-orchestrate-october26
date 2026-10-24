import csv, json

with open('dataset/sample_output.csv', newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        steps = json.loads(r['steps_json'])
        ev_ids = [s.get('evidence_id') for s in steps if s.get('evidence_id')]
        print(f"{r['case_id']} ({r['deletion_status']}): ev_ids = {set(ev_ids)}")
