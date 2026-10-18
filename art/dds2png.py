import sys
from pathlib import Path
from PIL import Image
src = Path(sys.argv[1]); out = Path(sys.argv[2])
names = sys.argv[3:]
tiles = []
for n in names:
    try:
        im = Image.open(src / f"{n}.dds").convert("RGB")
    except Exception as e:
        print("fail", n, e); continue
    im.save(out / f"{n}.png"); print(n, im.size)
    tiles.append((n, im))
# contact sheet
w = 400; h = 0
thumbs = []
for n, im in tiles:
    t = im.copy(); t.thumbnail((w, w)); thumbs.append(t); h = max(h, t.height)
cols = 4; rows = (len(thumbs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), "black")
for i, t in enumerate(thumbs):
    sheet.paste(t, ((i % cols) * w, (i // cols) * h))
sheet.save(out / "sheet.png")
