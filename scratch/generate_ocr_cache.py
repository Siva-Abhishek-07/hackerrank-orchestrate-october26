import os
import json
from rapidocr_onnxruntime import RapidOCR

engine = RapidOCR()
img_dir = 'dataset/evidence/images'

ocr_cache = {}
for f in sorted(os.listdir(img_dir)):
    if f.endswith('.png'):
        path = os.path.join(img_dir, f)
        result, _ = engine(path)
        texts = [item[1] for item in result] if result else []
        ocr_cache[f] = texts
        print(f"Done {f}: {len(texts)} lines", flush=True)

with open('scratch/ocr_cache.json', 'w', encoding='utf-8') as fp:
    json.dump(ocr_cache, fp, indent=2, ensure_ascii=False)

print("Saved scratch/ocr_cache.json successfully!", flush=True)
