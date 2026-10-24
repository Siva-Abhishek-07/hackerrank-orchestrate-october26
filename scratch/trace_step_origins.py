import json, csv, os, glob
from pathlib import Path
import pypdf

DATASET_DIR = Path("dataset")
samples = list(csv.DictReader(open(DATASET_DIR / "sample_deletion_requests.csv", encoding="utf-8")))
sample_out = {r['case_id']: r for r in csv.DictReader(open(DATASET_DIR / "sample_output.csv", encoding="utf-8"))}
activities = list(csv.DictReader(open(DATASET_DIR / "system_activity.csv", encoding="utf-8")))
ev_files = list(csv.DictReader(open(DATASET_DIR / "evidence_files.csv", encoding="utf-8")))
ev_by_id = {r['file_id']: r for r in ev_files}

# Load OCR cache
ocr_cache = json.load(open('scratch/ocr_cache.json', encoding='utf-8')) if os.path.exists('scratch/ocr_cache.json') else {}

# Load PDF texts
pdf_texts = {}
for p in glob.glob('dataset/evidence/documents/*.pdf'):
    fname = os.path.basename(p)
    reader = pypdf.PdfReader(p)
    pdf_texts[fname] = "".join(page.extract_text() or "" for page in reader.pages)

# Map file_id -> text content
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

# Check each sample case
for s in samples:
    cid = s['case_id']
    steps = json.loads(sample_out[cid]['steps_json'])
    status = sample_out[cid]['deletion_status']
    print(f"\n{'='*70}")
    print(f"{cid} | status: {status} | req: {s['requested_at']} | rep: {s['reported_at']} | audit: {s['audit_at']}")
    for step in steps:
        res = step['resource_id']
        sys_id = step['system_id']
        op = step['operation']
        phase = step['phase']
        ev_id = step['evidence_id']
        
        # Check where res appears in evidence
        in_evs = [f for f, txt in ev_text.items() if res in txt]
        
        # Check where res appears in activity
        in_acts = [f"{a['activity_id']}:{a['event_type']}:{a['reported_result']}@{a['event_time']}" for a in activities if a['resource_id'] == res]
        
        print(f"  {phase:<12} | {sys_id:<18} | {res:<16} | {op:<24} | ev={ev_id:<12} | in_evs={in_evs} | in_acts={in_acts[:2]}")
