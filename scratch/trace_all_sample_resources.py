import json
import pandas as pd
import os
import glob
import re
import pypdf

df_sample_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_sample_out = pd.read_csv('dataset/sample_output.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv').set_index('file_id')
df_activity = pd.read_csv('dataset/system_activity.csv')

# Load OCR cache
ocr_cache = {}
if os.path.exists('scratch/ocr_cache.json'):
    with open('scratch/ocr_cache.json', 'r', encoding='utf-8') as fp:
        ocr_cache = json.load(fp)

# Load PDF texts
pdf_texts = {}
for p in glob.glob('dataset/evidence/documents/*.pdf'):
    fname = os.path.basename(p)
    reader = pypdf.PdfReader(p)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    pdf_texts[fname] = text

# All evidence contents as text
ev_text_map = {}
for fid, r in df_ev.iterrows():
    fpath = os.path.join('dataset', r['file_path'])
    fname = os.path.basename(fpath)
    if fpath.endswith('.pdf'):
        ev_text_map[fid] = pdf_texts.get(fname, '')
    elif fpath.endswith('.png'):
        ev_text_map[fid] = " ".join(ocr_cache.get(fname, []))
    else:
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                ev_text_map[fid] = fp.read()
        except:
            ev_text_map[fid] = ''

# Check each resource in sample output
sample_res_origins = {}
for idx, r in df_sample_out.iterrows():
    cid = r['case_id']
    steps = json.loads(r['steps_json'])
    for s in steps:
        res = s['resource_id']
        if res not in sample_res_origins:
            in_act = df_activity[df_activity['resource_id'] == res]
            acts_list = [f"{a['activity_id']}:{a['event_type']}:{a['reported_result']}" for _, a in in_act.iterrows()]
            
            in_evs = [fid for fid, txt in ev_text_map.items() if res in txt]
            
            sample_res_origins[res] = {
                'in_activity': acts_list,
                'in_evidence': in_evs,
                'case': cid,
                'op': s['operation'],
                'phase': s['phase']
            }

print(f"Total unique resources: {len(sample_res_origins)}")
missing_all = 0
for res, info in sample_res_origins.items():
    if not info['in_activity'] and not info['in_evidence']:
        print(f"UNTRACKED RESOURCE: {res} in case {info['case']}")
        missing_all += 1

print(f"Total completely untracked resources: {missing_all}")
