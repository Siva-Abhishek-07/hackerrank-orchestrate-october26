import json
import pandas as pd
import os
import glob
import pypdf

df_sample_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_sample_out = pd.read_csv('dataset/sample_output.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv').set_index('file_id')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')

# Load OCR cache
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

# Identity mapping
user_map = {}
for _, u in df_users.iterrows():
    uid = u['user_id']
    user_map[uid] = {
        'emails': set([u['email'].strip().lower()]),
        'phones': set([u['phone'].strip()]) if pd.notna(u['phone']) else set(),
        'hashes': set([u['email_hash'].strip()]) if pd.notna(u['email_hash']) else set(),
        'name': u['name']
    }

email_to_uid = {}
for uid, info in user_map.items():
    for e in info['emails']:
        email_to_uid[e] = uid

for _, a in df_audit.iterrows():
    uid = a['user_id']
    if uid in user_map:
        fn = a['field_name']
        if fn == 'email':
            if pd.notna(a['old_value']):
                e = str(a['old_value']).strip().lower()
                user_map[uid]['emails'].add(e)
                email_to_uid[e] = uid
            if pd.notna(a['new_value']):
                e = str(a['new_value']).strip().lower()
                user_map[uid]['emails'].add(e)
                email_to_uid[e] = uid
        elif fn == 'phone':
            if pd.notna(a['old_value']): user_map[uid]['phones'].add(str(a['old_value']).strip())
            if pd.notna(a['new_value']): user_map[uid]['phones'].add(str(a['new_value']).strip())
        elif fn == 'email_hash':
            if pd.notna(a['old_value']): user_map[uid]['hashes'].add(str(a['old_value']).strip())
            if pd.notna(a['new_value']): user_map[uid]['hashes'].add(str(a['new_value']).strip())

# Test finding evidence files for each sample case
for idx, r in df_sample_req.iterrows():
    cid = r['case_id']
    e = r['email'].strip().lower()
    uid = email_to_uid[e]
    aud_at = r['audit_at']
    out_row = df_sample_out[df_sample_out['case_id'] == cid].iloc[0]
    steps = json.loads(out_row['steps_json'])
    gold_cited = set(s['evidence_id'] for s in steps if s['evidence_id'])
    
    # Check which evidence files captured before aud_at contain any identifier of this user
    matching_evs = []
    for fid, meta in df_ev.iterrows():
        if meta['captured_at'] <= aud_at:
            txt = ev_text_map[fid].lower()
            # check email, uid, or hashes
            found = False
            for em in user_map[uid]['emails']:
                if em in txt: found = True; break
            if not found and uid in txt:
                found = True
            if found:
                matching_evs.append(fid)
    
    print(f"{cid:<8} | uid={uid:<8} | gold_cited={list(gold_cited)} | matching_evs={matching_evs}")
