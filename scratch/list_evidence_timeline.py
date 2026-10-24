import csv

evs = list(csv.DictReader(open('dataset/evidence_files.csv', encoding='utf-8')))
evs.sort(key=lambda x: x['captured_at'])
for e in evs:
    print(f"{e['captured_at']} | {e['file_id']:<12} | {e['origin']:<42} | {e['file_path']}")
