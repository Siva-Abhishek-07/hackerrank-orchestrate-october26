import json, csv, os, sys, re
from pathlib import Path
from datetime import datetime
import pypdf

DATASET_DIR = Path("dataset")

# Load data
users = list(csv.DictReader(open(DATASET_DIR / "user_identities.csv", encoding="utf-8")))
audit_log = list(csv.DictReader(open(DATASET_DIR / "user_audit_log.csv", encoding="utf-8")))
samples = list(csv.DictReader(open(DATASET_DIR / "sample_deletion_requests.csv", encoding="utf-8")))
sample_out = {r['case_id']: r for r in csv.DictReader(open(DATASET_DIR / "sample_output.csv", encoding="utf-8"))}
activities = list(csv.DictReader(open(DATASET_DIR / "system_activity.csv", encoding="utf-8")))
ev_files = list(csv.DictReader(open(DATASET_DIR / "evidence_files.csv", encoding="utf-8")))
ev_by_id = {r['file_id']: r for r in ev_files}

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
        elif fn == 'phone':
            for v in [a.get('old_value'), a.get('new_value')]:
                if v: user_map[uid]['phones'].add(v.strip())
        elif fn == 'email_hash':
            for v in [a.get('old_value'), a.get('new_value')]:
                if v: user_map[uid]['hashes'].add(v.strip())

print("Testing exact user matching for case_03 and case_25...")
# Let's verify word boundary matching for user_25
pattern_25 = r'\buser_25\b'
print("Matches user_250?", bool(re.search(pattern_25, "user_250")))
print("Matches user_25?", bool(re.search(pattern_25, "user_25")))
