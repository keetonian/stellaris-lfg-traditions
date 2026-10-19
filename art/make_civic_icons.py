"""Builds the icons of this mod's civics: vanilla civic icons recoloured to one shared colour, so every LFG civic looks
the same and stands apart from vanilla's teal ones. The hue lives in CIVIC_COLOR; change it there and rerun.

Needs Pillow (reads and writes .dds); not part of the stdlib-only tooling. Run from the repo root:
  python3 art/make_civic_icons.py
"""
from pathlib import Path
from PIL import Image

GAME = Path.home() / "Library/Application Support/Steam/steamapps/common/Stellaris"
OUT = Path("mod/gfx/interface/icons/governments/civics")
CIVIC_COLOR = (240, 170, 40)  # amber; every LFG civic uses it
# our civic -> vanilla icon whose glyph it borrows
ICONS = {
    "civic_lfg_applied_biosciences": "civic_genetic_identification",
}


def recolour(im: Image.Image, color) -> Image.Image:
    """Keep the icon's light/dark pattern (hex, glyph, shading) but in `color`: each pixel's brightness (its HSV value,
    which keeps vanilla's vivid face bright, unlike luminance) scales `color`, stretched so the face reaches it fully."""
    value = im.convert("HSV").getchannel("V")
    scale = 255 / max(value.getextrema()[1], 1)
    channels = [value.point(lambda v, c=c: min(255, int(v * scale * c / 255))) for c in color]
    out = Image.merge("RGB", channels).convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


OUT.mkdir(parents=True, exist_ok=True)
for civic, src in ICONS.items():
    im = Image.open(GAME / "gfx/interface/icons/governments/civics" / f"{src}.dds").convert("RGBA")
    recolour(im, CIVIC_COLOR).save(OUT / f"{civic}.dds")
    print("wrote", OUT / f"{civic}.dds")
