import pandas as pd
from datetime import datetime, timedelta

df_sample_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_activity = pd.read_csv('dataset/system_activity.csv')

# Parse datetimes
df_activity['dt'] = pd.to_datetime(df_activity['event_time'])

deletion_worker_acts = df_activity[df_activity['source_system'] == 'deletion_worker']
print(f"Total deletion_worker activities: {len(deletion_worker_acts)}")

for idx, r in df_sample_req.head(10).iterrows():
    cid = r['case_id']
    req_dt = pd.to_datetime(r['requested_at'])
    rep_dt = pd.to_datetime(r['reported_at'])
    
    # Filter deletion_worker activities between requested_at - 1 hour and reported_at + 2 hours
    window_acts = deletion_worker_acts[(deletion_worker_acts['dt'] >= req_dt - timedelta(hours=1)) & 
                                       (deletion_worker_acts['dt'] <= rep_dt + timedelta(hours=2))]
    print(f"\n{cid} | requested: {r['requested_at']} | reported: {r['reported_at']} | found {len(window_acts)} acts in window:")
    for _, a in window_acts.iterrows():
        print(f"  {a['event_time']} | {a['event_type']} | {a['target_system']} | {a['resource_id']} | {a['reported_result']}")
