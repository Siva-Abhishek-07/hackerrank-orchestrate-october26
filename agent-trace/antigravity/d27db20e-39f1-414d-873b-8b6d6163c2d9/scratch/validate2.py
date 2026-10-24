#!/usr/bin/env python3
"""
Validate by running agent on sample_deletion_requests and comparing to sample_output.
"""
import csv
import json
import sys
import os
import importlib.util

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.getcwd()

# Import agent main
spec = importlib.util.spec_from_file_location("agent_main", os.path.join(REPO_ROOT, "code", "main.py"))
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)

DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_csv_dict(path):
    with open(path, newline='', encoding='utf-8') as f:
        return {r['case_id']: r for r in csv.DictReader(f)}

print("Loading data...")
users = load_csv(os.path.join(DATASET_DIR, "user_identities.csv"))
audit_log = load_csv(os.path.join(DATASET_DIR, "user_audit_log.csv"))
evidence_files_csv = load_csv(os.path.join(DATASET_DIR, "evidence_files.csv"))
sample_requests = load_csv(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"))
sample_output = load_csv_dict(os.path.join(DATASET_DIR, "sample_output.csv"))

print("Building identity index...")
email_to_uid, uid_to_user, uid_to_all_emails, uid_to_all_phones, uid_to_all_hashes = agent_module.build_identity_index(users, audit_log)

print("Building evidence index...")
evidence_index = agent_module.EvidenceIndex(evidence_files_csv, uid_to_all_emails, uid_to_all_phones, uid_to_user, uid_to_all_hashes)

print(f"Processing {len(sample_requests)} sample cases...\n")

correct_status = 0
wrong_status = 0

for case in sorted(sample_requests, key=lambda r: int(r['case_id'].split('_')[1])):
    case_id = case['case_id']
    email = case['email'].strip().lower()
    request_text = case.get('request_text', '')

    expected = sample_output.get(case_id, {})
    exp_status = expected.get('deletion_status', 'MISSING')
    exp_steps = json.loads(expected.get('steps_json', '[]'))

    # Classify deletion intent
    is_del = agent_module.is_deletion_request(request_text)
    if not is_del:
        got_status = 'NOT_APPLICABLE'
        got_steps = []
    else:
        uid = email_to_uid.get(email)
        if not uid:
            got_status = 'COMPLETE'
            got_steps = []
        else:
            user = uid_to_user.get(uid, {})
            try:
                got_status, steps_json = agent_module.process_case(
                    case, uid, user, uid_to_all_emails, uid_to_all_phones, uid_to_user, evidence_index
                )
                got_steps = json.loads(steps_json)
            except Exception as e:
                print(f"  ERROR in {case_id}: {e}")
                import traceback; traceback.print_exc()
                got_status = 'COMPLETE'
                got_steps = []

    status_match = exp_status == got_status
    if status_match:
        correct_status += 1
    else:
        wrong_status += 1

    mark = 'OK' if status_match else 'FAIL'
    print(f"{case_id}: expected={exp_status:15s} got={got_status:15s} [{mark}]")
    if not status_match:
        print(f"  Req text: {request_text[:80]}")
        print(f"  Expected steps ({len(exp_steps)}): {[s['operation'] for s in exp_steps[:4]]}")
        print(f"  Got steps ({len(got_steps)}): {[s['operation'] for s in got_steps[:4]]}")

print(f"\n=== SUMMARY ===")
print(f"Status accuracy: {correct_status}/{len(sample_requests)} ({100*correct_status/len(sample_requests):.1f}%)")
