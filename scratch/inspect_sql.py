import os
import glob
import re

sql_dir = 'dataset/evidence/databases'
sql_files = glob.glob(os.path.join(sql_dir, '*.sql'))
print(f"Total SQL files: {len(sql_files)}")

tables_found = set()
for f in sql_files:
    fname = os.path.basename(f)
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    # find CREATE TABLE
    creates = re.findall(r'CREATE TABLE\s+([a-zA-Z0-9_]+)', content, re.IGNORECASE)
    for c in creates:
        tables_found.add(c)
    # check line count
    lines = content.strip().split('\n')
    print(f"{fname:<45} | {len(lines)} lines | tables: {creates}")

print(f"\nAll unique table names across all SQL files: {sorted(list(tables_found))}")
