import json
import pandas as pd

df_sample_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_sample_out = pd.read_csv('dataset/sample_output.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv').set_index('file_id')

summary = []
for idx, r in df_sample_req.iterrows():
    cid = r['case_id']
    email = r['email']
    rep_st = r['reported_status']
    rep_at = r['reported_at']
    aud_at = r['audit_at']
    
    out_row = df_sample_out[df_sample_out['case_id'] == cid].iloc[0]
    del_st = out_row['deletion_status']
    steps = json.loads(out_row['steps_json'])
    
    # cited evidence
    cited = list(set(s['evidence_id'] for s in steps if s['evidence_id']))
    
    # resources per phase
    f_res = [(s['system_id'], s['resource_id'], s['operation']) for s in steps if s['phase'] == 'FINDING']
    r_res = [(s['system_id'], s['resource_id'], s['operation']) for s in steps if s['phase'] == 'REMEDIATION']
    v_res = [(s['system_id'], s['resource_id'], s['operation'], s['evidence_id']) for s in steps if s['phase'] == 'VERIFICATION']
    
    summary.append({
        'case_id': cid,
        'email': email,
        'del_status': del_st,
        'rep_status': rep_st,
        'rep_at': rep_at,
        'audit_at': aud_at,
        'cited': cited,
        'findings': f_res,
        'verifications': v_res
    })

for s in summary:
    print(f"\n{s['case_id']} | {s['del_status']} | rep={s['rep_status']} | audit={s['audit_at']} | cited={s['cited']}")
    if s['findings']:
        print(f"  Findings: {s['findings']}")
    print(f"  Verifications: {s['verifications']}")
