import os
from PIL import Image

for f in sorted(os.listdir('dataset/evidence/images')):
    if f.endswith('.png'):
        p = os.path.join('dataset/evidence/images', f)
        img = Image.open(p)
        print(f"{f}: {img.info}")
