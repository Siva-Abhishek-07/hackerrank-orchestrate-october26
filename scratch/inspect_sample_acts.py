import json, csv, os
from datetime import datetime, timedelta
from pathlib import Path

DATASET_DIR = Path("dataset")
samples = list(csv.DictReader(open(DATASET_DIR / "sample_deletion_requests.csv", encoding="utf-8")))
sample_out = {r['case_id']: r for r in csv.DictReader(open(DATASET_DIR / "sample_output.csv", encoding="utf-8"))}
activities = list(csv.DictReader(open(DATASET_DIR / "system_activity.csv", encoding="utf-8")))

users = list(csv.DictReader(open(DATASET_DIR / "user_identities.csv", encoding="utf-8")))
audit_log = list(csv.DictReader(open(DATASET_DIR / "user_audit_log.csv", encoding="utf-8")))

user_map = {}
for u in users:
    uid = u['user_id']
    user_map[uid] = {
        'uid': uid,
        'emails': {u['email'].strip().lower()} if u.get('email') else set(),
        'phones': {u['phone'].strip()} if u.get('phone') else set(),
        'hashes': {u['email_hash'].strip()} if u.get('email_hash') else set(),
        'name': u.get('name', '')
    }

email_to_uid = {}
for uid, info in user_map.items():
    for e in info['emails']: email_to_uid[e] = uid

for a in audit_log:
    uid = a['user_id']
    if uid in user_map:
        fn = a['field_name']
        if fn == 'email':
            for v in [a.get('old_value'), a.get('new_value')]:
                if v:
                    em = v.strip().lower()
                    user_map[uid]['emails'].add(em)
                    email_to_uid[em] = uid

# Parse activity timestamps
for a in activities:
    a['dt'] = datetime.fromisoformat(a['event_time'].replace('Z', '+00:00'))

for s in samples:
    cid = s['case_id']
    em = s['email'].strip().lower()
    uid = email_to_uid.get(em)
    steps = json.loads(sample_out[cid]['steps_json'])
    step_res = set(st['resource_id'] for st in steps)
    
    req_dt = datetime.fromisoformat(s['requested_at'].replace('Z', '+00:00'))
    rep_dt = datetime.fromisoformat(s['reported_at'].replace('Z', '+00:00'))
    aud_dt = datetime.fromisoformat(s['audit_at'].replace('Z', '+00:00'))
    
    # Check all activities matching step_res
    matching_acts = [a for a in activities if a['resource_id'] in step_res]
    
    # Check deletion worker activities around reported_at
    dw_near_rep = [a for a in activities if a['source_system'] == 'deletion_worker' and abs((a['dt'] - rep_dt).total_seconds()) <= 7200]
    
    # Check if any activities mention user_id or email
    user_acts = [a for a in activities if uid in a['details'] or any(e in a['details'].lower() for e in user_map[uid]['emails'])]
    
    print(f"\n{cid} ({uid}, {em}): gold_resources = {step_res}")
    print(f"  matching_acts ({len(matching_acts)}): {[(a['resource_id'], a['event_type'], a['reported_result'], a['event_time']) for a in matching_acts]}")
    if user_acts:
        print(f"  user_acts ({len(user_acts)}): {[(a['resource_id'], a['event_type'], a['event_time']) for a in user_acts]}")
