import csv

ev_map = {}
with open('dataset/evidence_files.csv', newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        ev_map[r['file_id']] = r

for fid in ['evidence_54', 'evidence_94', 'evidence_56', 'evidence_57', 'evidence_58', 'evidence_59', 'evidence_93', 'evidence_61', 'evidence_03', 'evidence_01', 'evidence_05', 'evidence_92', 'evidence_51']:
    print(fid, ev_map.get(fid))
