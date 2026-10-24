import json, csv, os, glob
from pathlib import Path

DATASET_DIR = Path("dataset")
samples = list(csv.DictReader(open(DATASET_DIR / "sample_deletion_requests.csv", encoding="utf-8")))
sample_out = {r['case_id']: r for r in csv.DictReader(open(DATASET_DIR / "sample_output.csv", encoding="utf-8"))}
ev_files = list(csv.DictReader(open(DATASET_DIR / "evidence_files.csv", encoding="utf-8")))
ev_by_id = {r['file_id']: r for r in ev_files}

# Build user identities map
users = list(csv.DictReader(open(DATASET_DIR / "user_identities.csv", encoding="utf-8")))
audit_log = list(csv.DictReader(open(DATASET_DIR / "user_audit_log.csv", encoding="utf-8")))

user_map = {}
for u in users:
    uid = u['user_id']
    user_map[uid] = {
        'uid': uid,
        'emails': {u['email'].strip().lower()} if u.get('email') else set(),
        'phones': {u['phone'].strip()} if u.get('phone') else set(),
        'hashes': {u['email_hash'].strip()} if u.get('email_hash') else set(),
        'name': u.get('name', '')
    }

email_to_uid = {}
for uid, info in user_map.items():
    for e in info['emails']: email_to_uid[e] = uid

for a in audit_log:
    uid = a['user_id']
    if uid in user_map:
        fn = a['field_name']
        if fn == 'email':
            for v in [a.get('old_value'), a.get('new_value')]:
                if v:
                    em = v.strip().lower()
                    user_map[uid]['emails'].add(em)
                    email_to_uid[em] = uid
        elif fn == 'phone':
            for v in [a.get('old_value'), a.get('new_value')]:
                if v: user_map[uid]['phones'].add(v.strip())
        elif fn == 'email_hash':
            for v in [a.get('old_value'), a.get('new_value')]:
                if v: user_map[uid]['hashes'].add(v.strip())

# Load OCR cache and PDF texts
ocr_cache = json.load(open('scratch/ocr_cache.json', encoding='utf-8')) if os.path.exists('scratch/ocr_cache.json') else {}
import pypdf
pdf_texts = {}
for p in glob.glob('dataset/evidence/documents/*.pdf'):
    fname = os.path.basename(p)
    reader = pypdf.PdfReader(p)
    pdf_texts[fname] = "".join(page.extract_text() or "" for page in reader.pages)

ev_text = {}
for r in ev_files:
    fid = r['file_id']
    fpath = DATASET_DIR / r['file_path']
    fname = fpath.name
    if fpath.suffix == '.pdf':
        ev_text[fid] = pdf_texts.get(fname, '')
    elif fpath.suffix == '.png':
        ev_text[fid] = " ".join(ocr_cache.get(fname, []))
    else:
        try:
            ev_text[fid] = fpath.read_text(encoding='utf-8', errors='ignore')
        except:
            ev_text[fid] = ''

# For each sample case, check which evidence files <= audit_at contain user identifiers
correct_ev_count = 0
for s in samples:
    cid = s['case_id']
    em = s['email'].strip().lower()
    uid = email_to_uid.get(em)
    info = user_map[uid]
    audit_at = s['audit_at']
    gold_steps = json.loads(sample_out[cid]['steps_json'])
    gold_evs = set(st['evidence_id'] for st in gold_steps if st['evidence_id'])
    
    # Check matching evidence files
    matching = []
    for fid, meta in ev_by_id.items():
        if meta['captured_at'] <= audit_at:
            txt = ev_text[fid].lower()
            # check if any user email, phone, uid, or hash is in txt
            is_match = False
            for email in info['emails']:
                if email in txt: is_match = True; break
            if not is_match and uid in txt:
                is_match = True
            for phone in info['phones']:
                if phone and phone.lower() in txt: is_match = True; break
            
            if is_match:
                matching.append((meta['captured_at'], fid))
    
    # Sort matching by captured_at desc (most recent first)
    matching.sort(key=lambda x: x[0], reverse=True)
    top_evs = [x[1] for x in matching[:3]]
    
    # Check if gold_evs is subset of top_evs or matching
    matched_gold = gold_evs.issubset(set(top_evs)) or (not gold_evs)
    if matched_gold:
        correct_ev_count += 1
    print(f"{cid:<8} | uid={uid:<8} | gold={list(gold_evs)} | top_evs={top_evs} | match={matched_gold}")

print(f"\nTotal matched: {correct_ev_count}/{len(samples)}")
