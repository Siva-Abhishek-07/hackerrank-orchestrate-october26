import json
import pandas as pd

df_sample_out = pd.read_csv('dataset/sample_output.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv').set_index('file_id')

cited_ev = {}
for idx, r in df_sample_out.iterrows():
    case_id = r['case_id']
    steps = json.loads(r['steps_json'])
    for s in steps:
        ev_id = s.get('evidence_id', '')
        if ev_id:
            cited_ev.setdefault(ev_id, []).append((case_id, s['phase'], s['operation'], s['resource_id']))

print(f"Total unique evidence_ids cited in sample_output: {len(cited_ev)}")
for ev_id, cases in cited_ev.items():
    if ev_id in df_ev.index:
        meta = df_ev.loc[ev_id]
        print(f"{ev_id:<12} | {meta['captured_at']} | {meta['file_path']} | Used in {len(cases)} steps across cases: {sorted(list(set([c[0] for c in cases])))}")
    else:
        print(f"{ev_id:<12} | NOT IN evidence_files.csv | Used in {len(cases)} steps")
