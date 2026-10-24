import json
import pandas as pd
from datetime import datetime

df_sample_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_sample_out = pd.read_csv('dataset/sample_output.csv')
df_activity = pd.read_csv('dataset/system_activity.csv')

df_activity['dt'] = pd.to_datetime(df_activity['event_time'])
deletion_worker_acts = df_activity[df_activity['source_system'] == 'deletion_worker']

# Check for each sample case: what was the primary account_id in sample_output?
for idx, r in df_sample_req.iterrows():
    cid = r['case_id']
    req_dt = pd.to_datetime(r['requested_at'])
    rep_dt = pd.to_datetime(r['reported_at'])
    
    out_row = df_sample_out[df_sample_out['case_id'] == cid].iloc[0]
    steps = json.loads(out_row['steps_json'])
    gold_accounts = [s['resource_id'] for s in steps if s['system_id'] == 'account_service']
    
    # Check deletion worker activities on account_service around reported_at
    # (say within [requested_at - 1h, reported_at + 2h])
    acts = deletion_worker_acts[(deletion_worker_acts['dt'] >= req_dt - pd.Timedelta(hours=1)) & 
                                (deletion_worker_acts['dt'] <= rep_dt + pd.Timedelta(hours=2)) &
                                (deletion_worker_acts['target_system'] == 'account_service')]
    
    act_accounts = list(acts['resource_id'])
    print(f"{cid:<8} | rep_at: {r['reported_at']} | gold_account: {gold_accounts} | act_accounts: {act_accounts}")
