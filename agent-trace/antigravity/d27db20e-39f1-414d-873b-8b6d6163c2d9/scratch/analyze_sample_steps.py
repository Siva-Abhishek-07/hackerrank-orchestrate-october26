import json
import pandas as pd

df_sample_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_sample_out = pd.read_csv('dataset/sample_output.csv')
df_ev_files = pd.read_csv('dataset/evidence_files.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
df_activity = pd.read_csv('dataset/system_activity.csv')

print(f"Total evidence files: {len(df_ev_files)}")
print(f"Total activities: {len(df_activity)}")

# For each sample case, let's print all steps
for idx, r in df_sample_out.iterrows():
    case_id = r['case_id']
    status = r['deletion_status']
    steps = json.loads(r['steps_json'])
    req_row = df_sample_req[df_sample_req['case_id'] == case_id].iloc[0]
    print(f"\n==========================================")
    print(f"CASE: {case_id} | Status: {status} | Req Email: {req_row['email']} | Audit At: {req_row['audit_at']}")
    for s in steps:
        print(f"  Step {s['step_no']}: [{s['phase']}] {s['system_id']} | {s['resource_id']} | {s['operation']} | {s['state']} | ev: {s['evidence_id']}")
