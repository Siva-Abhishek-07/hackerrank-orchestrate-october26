#!/usr/bin/env python3
"""Debug specific cases."""
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
sample_requests = {r['case_id']:r for r in load_csv(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"))}
sample_output = {r['case_id']:r for r in load_csv(os.path.join(DATASET_DIR, "sample_output.csv"))}

email_to_uid, uid_to_user, uid_to_all_emails, uid_to_all_phones = agent_module.build_identity_index(users, audit_log)
evidence_index = agent_module.EvidenceIndex(evidence_files_csv, uid_to_all_emails, uid_to_all_phones, uid_to_user)

from datetime import datetime, timezone

# Debug cases with wrong results
debug_cases = ['case_03', 'case_09', 'case_07', 'case_13', 'case_14', 'case_16', 'case_19']

for case_id in debug_cases:
    case = sample_requests.get(case_id)
    if not case:
        continue
    expected = sample_output.get(case_id, {})
    exp_status = expected.get('deletion_status', '?')
    exp_steps = json.loads(expected.get('steps_json', '[]'))

    email = case['email'].strip().lower()
    uid = email_to_uid.get(email)
    audit_at = case['audit_at']
    audit_at_ts = agent_module.parse_ts(audit_at)

    print(f"\n{'='*60}")
    print(f"CASE: {case_id} | Expected: {exp_status} | Email: {email} | UID: {uid}")
    print(f"Request: {case['request_text'][:100]}")
    print(f"Is deletion: {agent_module.is_deletion_request(case['request_text'])}")

    if not uid:
        print("  No UID found!")
        continue

    emails = uid_to_all_emails.get(uid, set())
    phones = uid_to_all_phones.get(uid, set())
    emails_lower = {e.lower() for e in emails if e}
    print(f"  Emails: {emails_lower}")

    # Find best evidence files
    best_ev = agent_module.find_best_evidence_files(audit_at_ts, evidence_index)
    print(f"  Best evidence (first 5): {best_ev[:5]}")

    # Search first few evidence files
    for ev_id in best_ev[:5]:
        found = evidence_index.find_user_records_in_evidence(ev_id, uid, emails_lower, phones, uid)
        if found:
            print(f"  Evidence {ev_id}: found {len(found)} records:")
            for rec in found[:5]:
                print(f"    system={rec['system_id']}, rid={rec['resource_id']}, state={rec['state']}")

    print(f"  Expected steps: {[(s['operation'], s['system_id'], s['resource_id']) for s in exp_steps[:4]]}")
