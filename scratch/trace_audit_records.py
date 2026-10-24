import json
import pandas as pd
import glob
import os

df_sample_out = pd.read_csv('dataset/sample_output.csv')
df_sample_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_activity = pd.read_csv('dataset/system_activity.csv')

# Find all audit_records in sample_output
audit_records = {}
for idx, r in df_sample_out.iterrows():
    cid = r['case_id']
    steps = json.loads(r['steps_json'])
    for s in steps:
        if s['resource_id'].startswith('audit_record_'):
            audit_records[cid] = (s['resource_id'], s['evidence_id'], s['state'])

print(f"Total cases with audit_record: {len(audit_records)}")
for cid, (aid, evid, st) in audit_records.items():
    # Search aid in system_activity
    in_act = df_activity[df_activity['resource_id'] == aid]
    act_str = f"{len(in_act)} in activity" if len(in_act) else "NOT in activity"
    
    # Search aid in dataset/evidence
    matches = []
    for root, dirs, files in os.walk('dataset/evidence'):
        for f in files:
            p = os.path.join(root, f)
            try:
                with open(p, 'rb') as fp:
                    if aid.encode() in fp.read():
                        matches.append(f)
            except:
                pass
    ev_str = f"in {matches}" if matches else "NOT in evidence files"
    print(f"{cid:<10} | {aid:<20} | evid: {evid:<12} | {act_str:<16} | {ev_str}")
