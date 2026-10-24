import csv
from collections import Counter

evs = list(csv.DictReader(open('dataset/evidence_files.csv', encoding='utf-8')))
print("Total evidence files:", len(evs))
origins = Counter(r['origin'] for r in evs)
for orig, count in origins.most_common():
    print(f"  {orig:<45}: {count}")

exts = Counter(r['file_path'].split('.')[-1] for r in evs)
print("\nExtensions:")
for ext, count in exts.most_common():
    print(f"  .{ext:<10}: {count}")
