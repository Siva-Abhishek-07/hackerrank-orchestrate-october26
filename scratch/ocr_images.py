import os
from rapidocr_onnxruntime import RapidOCR

engine = RapidOCR()
img_dir = 'dataset/evidence/images'

for f in sorted(os.listdir(img_dir)):
    if f.endswith('.png'):
        path = os.path.join(img_dir, f)
        result, elapse = engine(path)
        print(f"\n==========================================")
        print(f"IMAGE: {f} (found {len(result) if result else 0} text boxes)")
        if result:
            for box, text, score in result[:15]:
                print(f"  [{score:.2f}] {text}")
            if len(result) > 15:
                print(f"  ... and {len(result) - 15} more lines")
