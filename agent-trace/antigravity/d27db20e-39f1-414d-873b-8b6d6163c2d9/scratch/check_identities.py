import pandas as pd

df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
df_sample = pd.read_csv('dataset/sample_deletion_requests.csv')
df_req = pd.read_csv('dataset/deletion_requests.csv')

print(f"Users count: {len(df_users)}")
print(f"Audit log rows: {len(df_audit)}")
print(f"Audit log field names: {df_audit['field_name'].value_counts().to_dict()}")

# Map email to user_id
email_to_user = {}
for _, r in df_users.iterrows():
    email_to_user[r['email'].strip().lower()] = r['user_id']

# Map historical emails from audit log
hist_email_to_user = {}
for _, r in df_audit.iterrows():
    if r['field_name'] == 'email':
        if pd.notna(r['old_value']):
            hist_email_to_user[str(r['old_value']).strip().lower()] = r['user_id']
        if pd.notna(r['new_value']):
            hist_email_to_user[str(r['new_value']).strip().lower()] = r['user_id']

# Check how many sample cases match
sample_matched = 0
for _, r in df_sample.iterrows():
    e = r['email'].strip().lower()
    uid = email_to_user.get(e) or hist_email_to_user.get(e)
    if uid:
        sample_matched += 1
    else:
        print(f"Unmatched sample email: {e} in {r['case_id']}")
print(f"Sample matched: {sample_matched}/{len(df_sample)}")

# Check how many eval requests match
req_matched = 0
unmatched_eval = []
for _, r in df_req.iterrows():
    e = r['email'].strip().lower()
    uid = email_to_user.get(e) or hist_email_to_user.get(e)
    if uid:
        req_matched += 1
    else:
        unmatched_eval.append((r['case_id'], e))
print(f"Eval matched: {req_matched}/{len(df_req)}")
if unmatched_eval:
    print(f"Unmatched eval (first 10): {unmatched_eval[:10]}")
