import json, glob, os

for p in glob.glob('dataset/evidence/**/*.json', recursive=True):
    fname = os.path.basename(p)
    try:
        data = json.load(open(p, encoding='utf-8'))
        if isinstance(data, dict):
            print(f"{fname:<45}: keys={list(data.keys())[:5]}, collection={data.get('collection')}, source={data.get('source')}")
        elif isinstance(data, list):
            print(f"{fname:<45}: list of {len(data)} items")
    except Exception as e:
        print(f"{fname:<45}: ERROR {e}")
