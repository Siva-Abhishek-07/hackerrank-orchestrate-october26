import json
import pandas as pd

df_sample_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_sample_out = pd.read_csv('dataset/sample_output.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
df_activity = pd.read_csv('dataset/system_activity.csv')

# Build mapping from email -> user
email_map = {}
for _, u in df_users.iterrows():
    email_map[u['email'].strip().lower()] = u['user_id']
for _, a in df_audit.iterrows():
    if a['field_name'] == 'email':
        if pd.notna(a['old_value']):
            email_map[str(a['old_value']).strip().lower()] = a['user_id']
        if pd.notna(a['new_value']):
            email_map[str(a['new_value']).strip().lower()] = a['user_id']

with open('scratch/deep_sample_inspection_utf8.txt', 'w', encoding='utf-8') as out_f:
    for idx, r in df_sample_req.iterrows():
        cid = r['case_id']
        email = r['email'].strip().lower()
        uid = email_map.get(email)
        out_row = df_sample_out[df_sample_out['case_id'] == cid].iloc[0]
        status = out_row['deletion_status']
        steps = json.loads(out_row['steps_json'])
        
        step_res = set(s['resource_id'] for s in steps)
        act_matches = df_activity[df_activity['resource_id'].isin(step_res)]
        
        out_f.write(f"\n=======================================================\n")
        out_f.write(f"CASE: {cid} | User: {uid} ({email}) | Reported: {r['reported_status']} @ {r['reported_at']} | Audit: {r['audit_at']}\n")
        out_f.write(f"Status: {status} | Steps Count: {len(steps)}\n")
        for s in steps:
            out_f.write(f"  Step {s['step_no']:<2} | {s['phase']:<12} | {s['system_id']:<20} | {s['resource_id']:<20} | {s['operation']:<25} | {s['state']:<10} | {s['evidence_id']}\n")
        
        if len(act_matches) > 0:
            out_f.write(f"  System activities for these resources ({len(act_matches)}):\n")
            for _, a in act_matches.iterrows():
                out_f.write(f"    [{a['activity_id']}] {a['event_time']} | {a['event_type']:<20} | {a['source_system']} -> {a['target_system']} | {a['resource_id']} | {a['reported_result']} | {a['details']}\n")

print("Wrote scratch/deep_sample_inspection_utf8.txt")
