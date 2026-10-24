import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
merged = pd.merge(df_req, df_out, on='case_id')

print(f"Total sample cases: {len(merged)}")
for idx, row in merged.iterrows():
    steps = json.loads(row['steps_json'])
    ops = [s['operation'] for s in steps]
    print(f"{row['case_id']} | Status: {row['deletion_status']:<15} | Steps: {len(steps)} | Ops: {ops}")
