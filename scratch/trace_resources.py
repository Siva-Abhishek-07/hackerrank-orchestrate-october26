import json
import pandas as pd
import glob
import os

df_sample_out = pd.read_csv('dataset/sample_output.csv')
df_activity = pd.read_csv('dataset/system_activity.csv')

# Collect all resource_ids from sample_output
sample_resources = {}
for idx, r in df_sample_out.iterrows():
    case_id = r['case_id']
    steps = json.loads(r['steps_json'])
    for s in steps:
        res = s['resource_id']
        sample_resources.setdefault(res, []).append((case_id, s['phase'], s['operation'], s['system_id'], s['evidence_id']))

print(f"Unique resources in sample output: {len(sample_resources)}")

# Check where they appear in system_activity
found_in_activity = {}
for res in sample_resources:
    acts = df_activity[df_activity['resource_id'] == res]
    if len(acts) > 0:
        found_in_activity[res] = acts[['activity_id', 'event_time', 'event_type', 'source_system', 'target_system', 'reported_result']].to_dict('records')

print(f"Resources found in system_activity: {len(found_in_activity)} / {len(sample_resources)}")

# For resources not in system_activity, where are they?
missing_from_activity = [r for r in sample_resources if r not in found_in_activity]
print(f"Missing from system_activity: {len(missing_from_activity)}")
if missing_from_activity:
    print(f"Examples missing: {missing_from_activity[:15]}")
