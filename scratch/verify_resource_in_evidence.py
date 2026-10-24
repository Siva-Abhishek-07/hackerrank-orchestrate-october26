import json
import pandas as pd
import os

df_sample_out = pd.read_csv('dataset/sample_output.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv').set_index('file_id')

all_verified = True
for idx, r in df_sample_out.iterrows():
    cid = r['case_id']
    steps = json.loads(r['steps_json'])
    for s in steps:
        ev_id = s.get('evidence_id', '')
        res_id = s['resource_id']
        if ev_id:
            # Check if res_id is in the evidence file
            fpath = os.path.join('dataset', df_ev.loc[ev_id, 'file_path'])
            # Read file as text/bytes
            with open(fpath, 'rb') as fp:
                content = fp.read()
            if res_id.encode('utf-8') in content:
                pass
            else:
                print(f"[{cid}] Resource {res_id} NOT found in cited evidence {ev_id} ({fpath})!")
                all_verified = False

if all_verified:
    print("ALL resources in sample output steps with evidence_id were FOUND in their cited evidence files!")
