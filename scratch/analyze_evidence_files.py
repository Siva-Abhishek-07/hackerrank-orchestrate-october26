import pandas as pd
import os

df_ev = pd.read_csv('dataset/evidence_files.csv')
print(f"Total evidence files: {len(df_ev)}")

extensions = {}
for idx, r in df_ev.iterrows():
    ext = os.path.splitext(r['file_path'])[1]
    extensions.setdefault(ext, []).append((r['file_id'], r['file_path'], r['captured_at']))

for ext, files in extensions.items():
    print(f"\nExtension {ext}: {len(files)} files")
    for fid, fpath, cap in files[:5]:
        print(f"  {fid} | {cap} | {fpath}")
    if len(files) > 5:
        print(f"  ... and {len(files) - 5} more")
