import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src, cx, out = Path(sys.argv[1]), float(sys.argv[2]), Path(sys.argv[3])
im = Image.open(src).convert("RGB")
side = im.height  # 1080
left = int(max(0, min(im.width - side, cx * im.width - side / 2)))
im = im.crop((left, 0, left + side, side)).resize((640, 640), Image.LANCZOS)
# darken the bottom for the title
grad = Image.new("L", (1, 640))
for y in range(640):
    grad.putpixel((0, y), int(max(0, (y - 380) / 260) ** 1.3 * 220))
shade = Image.new("RGB", im.size, (5, 8, 14))
im = Image.composite(shade, im, grad.resize(im.size))
d = ImageDraw.Draw(im)
size = 80
while True:  # largest Heavy title that fits in 560 px
    title = ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", size, index=8)
    if d.textlength("LFG TRADITIONS", font=title) + 3 * 13 <= 560:
        break
    size -= 2
sub = ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", 24, index=5)
def centred(text, font, y, fill, spacing=0):
    w = d.textlength(text, font=font) + spacing * (len(text) - 1)
    x = (640 - w) / 2
    for ch in text:
        d.text((x + 2, y + 3), ch, font=font, fill=(0, 0, 0))
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + spacing
centred("LFG TRADITIONS", title, 482, (240, 214, 150), spacing=3)
centred("FOR GIGASTRUCTURAL ENGINEERING", sub, 566, (200, 215, 225), spacing=3)
im.save(out, optimize=True)
print(out, out.stat().st_size)
