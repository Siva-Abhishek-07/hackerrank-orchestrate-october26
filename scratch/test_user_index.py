import json, csv, os, glob
from pathlib import Path
import pypdf

DATASET_DIR = Path("dataset")
users = list(csv.DictReader(open(DATASET_DIR / "user_identities.csv", encoding="utf-8")))
audit_log = list(csv.DictReader(open(DATASET_DIR / "user_audit_log.csv", encoding="utf-8")))

# Build user index
user_info = {}
for u in users:
    uid = u['user_id']
    user_info[uid] = {
        'uid': uid,
        'emails': {u['email'].strip().lower()} if u.get('email') else set(),
        'phones': {u['phone'].strip()} if u.get('phone') else set(),
        'hashes': {u['email_hash'].strip()} if u.get('email_hash') else set(),
        'name': u.get('name', '')
    }

for a in audit_log:
    uid = a['user_id']
    if uid in user_info:
        fn = a['field_name']
        if fn == 'email':
            for v in [a.get('old_value'), a.get('new_value')]:
                if v: user_info[uid]['emails'].add(v.strip().lower())
        elif fn == 'phone':
            for v in [a.get('old_value'), a.get('new_value')]:
                if v: user_info[uid]['phones'].add(v.strip())
        elif fn == 'email_hash':
            for v in [a.get('old_value'), a.get('new_value')]:
                if v: user_info[uid]['hashes'].add(v.strip())

# Check user_01 through user_10 in evidence
samples = list(csv.DictReader(open(DATASET_DIR / "sample_deletion_requests.csv", encoding="utf-8")))
email_to_uid = {}
for uid, info in user_info.items():
    for e in info['emails']:
        email_to_uid[e] = uid

for s in samples[:5]:
    cid = s['case_id']
    em = s['email'].strip().lower()
    uid = email_to_uid.get(em)
    info = user_info.get(uid, {})
    print(f"\n{cid} | {em} -> {uid}: {info}")
