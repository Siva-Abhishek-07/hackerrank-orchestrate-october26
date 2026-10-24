import os
from PIL import Image

img_dir = 'dataset/evidence/images'
for f in os.listdir(img_dir):
    if f.endswith('.png'):
        path = os.path.join(img_dir, f)
        img = Image.open(path)
        print(f"Image: {f} | Size: {img.size} | Mode: {img.mode}")
        # Check if there is info/metadata
        if img.info:
            print(f"  Info keys: {list(img.info.keys())}")
