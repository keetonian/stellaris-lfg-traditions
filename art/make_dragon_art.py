"""Legendary Dragons art (Here Be Dragons): the dragon from vanilla's Here Be Dragons origin icon, in legendary gold.

- ascension perk icon (52x60): a vanilla perk icon's hexagon (its alpha) filled with a dark-to-gold gradient, the dragon
  on top;
- decision icon (45x45): the origin icon's diamond and dragon, tinted gold.

Needs Pillow; run from the repo root:
  python3 art/make_dragon_art.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from make_megastructure_icons import GAME, tint  # noqa: E402

GOLD = (255, 214, 110)
ORIGIN = GAME / "gfx/interface/icons/origins/origin_here_be_dragons.dds"
PERK_SHAPE = GAME / "gfx/interface/icons/ascension_perks/ap_boarding_pods.dds"


def dragon_mask(size: int) -> Image.Image:
    """The dragon: the origin icon's brightest pixels (the diamond's frame and fill are darker)."""
    src = Image.open(ORIGIN).convert("RGBA").resize((size, size), Image.LANCZOS)
    lum = src.convert("L")
    return lum.point(lambda v: 0 if v < 85 else min(255, (v - 85) * 5))


def perk_icon() -> Image.Image:
    shape = Image.open(PERK_SHAPE).convert("RGBA")
    w, h = shape.size
    bg = Image.new("RGBA", (w, h))
    px = bg.load()
    for y in range(h):
        t = y / h
        for x in range(w):
            px[x, y] = (int(25 + 45 * (1 - t)), int(14 + 25 * (1 - t)), int(10 + 8 * (1 - t)), 255)
    size = int(w * 1.05)
    mask = dragon_mask(size)
    glow = mask.filter(ImageFilter.GaussianBlur(2))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.paste(Image.new("RGBA", (size, size), (255, 150, 40, 255)), ((w - size) // 2, (h - size) // 2), glow)
    layer.paste(Image.new("RGBA", (size, size), GOLD + (255,)), ((w - size) // 2, (h - size) // 2), mask)
    out = Image.alpha_composite(bg, layer)
    out.putalpha(shape.getchannel("A"))
    return out


def decision_icon() -> Image.Image:
    return tint(Image.open(ORIGIN).convert("RGBA"), GOLD, keep=0.0).resize((45, 45), Image.LANCZOS)


ICONS = {
    Path("mod/gfx/interface/icons/ascension_perks/ap_lfg_legendary_dragons.dds"): perk_icon,
    Path("mod/gfx/interface/icons/decisions/decision_lfg_legendary_dragon.dds"): decision_icon,
}

if __name__ == "__main__":
    for path, make in ICONS.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        make().save(path)
    print(f"wrote {len(ICONS)} icons")
