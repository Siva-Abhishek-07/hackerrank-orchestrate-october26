#!/usr/bin/env python3
"""Debug evidence matching for case_03."""
import csv, json, sys, os, importlib.util
sys.stdout.reconfigure(encoding='utf-8')

spec = importlib.util.spec_from_file_location("agent_main", os.path.join(os.getcwd(), "code", "main.py"))
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)

DATASET_DIR = os.path.join(os.getcwd(), "dataset")

def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

users = load_csv(os.path.join(DATASET_DIR, "user_identities.csv"))
audit_log = load_csv(os.path.join(DATASET_DIR, "user_audit_log.csv"))
evidence_files_csv = load_csv(os.path.join(DATASET_DIR, "evidence_files.csv"))

email_to_uid, uid_to_user, uid_to_all_emails, uid_to_all_phones = agent_module.build_identity_index(users, audit_log)
evidence_index = agent_module.EvidenceIndex(evidence_files_csv, uid_to_all_emails, uid_to_all_phones, uid_to_user)

# case_03: user_43, email l.fontaine46@yahoo.com
uid = 'user_43'
emails = {'l.fontaine46@yahoo.com'}
phones = set()

# Load evidence_92 and manually search
ev92_data = agent_module.load_json_file(os.path.join(DATASET_DIR, 'evidence/records/service_resource_export_20260915_114455.json'))
svc_exports = ev92_data['service_exports']

print("Searching evidence_92 for user_43 (email: l.fontaine46@yahoo.com)")
print()
for svc_name, svc_data in svc_exports.items():
    for coll_name, records in svc_data.items():
        for rec in records:
            rec_str = json.dumps(rec).lower()
            if 'user_43' in rec_str or 'l.fontaine46@yahoo.com' in rec_str:
                print(f"FOUND in {svc_name}/{coll_name}: {json.dumps(rec)[:200]}")

print()
print("Looking at account_service/profile_lookups:")
for rec in svc_exports.get('account_service', {}).get('profile_lookups', []):
    print(" ", json.dumps(rec)[:200])

print()
print("Looking at analytics_platform/profiles:")
for rec in svc_exports.get('analytics_platform', {}).get('profiles', []):
    print(" ", json.dumps(rec)[:200])

# Check the actual expected resource IDs
print()
print("Searching all services for account_7566 / audit_record_2016 / analytics_9406:")
for svc_name, svc_data in svc_exports.items():
    for coll_name, records in svc_data.items():
        for rec in records:
            rid = rec.get('resource_id','')
            if rid in ['account_7566', 'audit_record_2016', 'analytics_9406']:
                print(f"FOUND {rid} in {svc_name}/{coll_name}: {json.dumps(rec)[:300]}")
