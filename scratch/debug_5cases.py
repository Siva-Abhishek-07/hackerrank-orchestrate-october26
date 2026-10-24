import csv, json
import datetime
import os
import sys

import importlib.util
spec = importlib.util.spec_from_file_location("agent_main", os.path.join(os.getcwd(), "code", "main.py"))
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)

build_identity_index = agent_module.build_identity_index
EvidenceIndex = agent_module.EvidenceIndex
load_csv = agent_module.load_csv
find_best_evidence_files = agent_module.find_best_evidence_files


parse_ts = agent_module.parse_ts

users = load_csv('dataset/user_identities.csv')
audit_log = load_csv('dataset/user_audit_log.csv')
evidence_files_csv = load_csv('dataset/evidence_files.csv')
sample_requests = {r['case_id']: r for r in load_csv('dataset/sample_deletion_requests.csv')}

email_to_uid, uid_to_user, uid_to_all_emails, uid_to_all_phones = build_identity_index(users, audit_log)
evidence_index = EvidenceIndex(evidence_files_csv, uid_to_all_emails, uid_to_all_phones, uid_to_user)

for cid in ['case_03', 'case_10', 'case_12', 'case_15', 'case_17']:
    case = sample_requests[cid]
    email = case['email'].strip().lower()
    uid = email_to_uid.get(email)
    print(f"*** {cid} (user={uid}, email={email}, audit_at={case['audit_at']}) ***")
    emails = uid_to_all_emails.get(uid, set())
    phones = uid_to_all_phones.get(uid, set())
    print(f"  all emails: {emails}, phones: {phones}")
    audit_at_ts = parse_ts(case['audit_at'])
    matching, other = find_best_evidence_files(audit_at_ts, evidence_index, uid, {e.lower() for e in emails}, phones)
    print(f"  matching files count: {len(matching)}")
    for age, ev_id, recs in matching:
        print(f"    ev_id={ev_id}, age={age:.1f}s, recs={recs}")
