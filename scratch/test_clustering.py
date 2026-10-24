import pandas as pd
from datetime import datetime

df_sample_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_req = pd.read_csv('dataset/deletion_requests.csv')
df_activity = pd.read_csv('dataset/system_activity.csv')

df_activity['dt'] = pd.to_datetime(df_activity['event_time'])
deletion_acts = df_activity[df_activity['source_system'] == 'deletion_worker'].copy()

# Sort by event_time
deletion_acts = deletion_acts.sort_values('dt')

print(f"Total deletion worker activities: {len(deletion_acts)}")

# Check time gaps between consecutive activities to find clusters
deletion_acts['time_diff'] = deletion_acts['dt'].diff()
print(f"Time diff quantiles:\n{deletion_acts['time_diff'].describe()}")

# Let's inspect activities around reported_at for all 32 sample cases
matched_counts = []
for idx, r in df_sample_req.iterrows():
    rep_dt = pd.to_datetime(r['reported_at'])
    # Check activities within 3 hours of reported_at
    near_acts = deletion_acts[(deletion_acts['dt'] >= rep_dt - pd.Timedelta(hours=3)) & 
                              (deletion_acts['dt'] <= rep_dt + pd.Timedelta(hours=3))]
    matched_counts.append(len(near_acts))

print(f"\nSample cases near reported_at activity count min={min(matched_counts)}, max={max(matched_counts)}, avg={sum(matched_counts)/len(matched_counts):.1f}")
