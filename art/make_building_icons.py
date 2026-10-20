"""Builds the Nanite Forge buildings' icons from vanilla / Gigastructural art, in the nanite style of
art/make_component_icons.py:

- Nanite Consensus Node 1-4 (78x78): vanilla's Brain Node 1 (the mechanical one) without its research flask, its yellow
  undergrowth turned into grey goo, vanilla's unity symbol where the flask was; higher tiers glow more and show 1-4 pips.
- Nanotensile Converter 1-2 (78x78): Gigastructural's megaworkshop with the nanite and supertensile symbols side by side
  (its own supertensile symbol removed); the upgrade glows cyan.
- Ancient Nanite Harvester (58x58, a starbase module icon): vanilla's nanite harvester module in ancient bronze with a
  cyan nanite glow.

Needs Pillow; run from the repo root:
  python3 art/make_building_icons.py
"""
from __future__ import annotations

import colorsys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

from make_component_icons import GAME, SEAM, glow, motes

GIGA = Path.home() / "Library/Application Support/Steam/steamapps/workshop/content/281990/1121692237"
BUILDINGS = Path("mod/gfx/interface/icons/buildings")
MODULES = Path("mod/gfx/interface/icons/modules")
GOO_DARK, GOO_LIGHT = (40, 46, 52), (170, 182, 190)


def load(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def clear(im: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    ImageDraw.Draw(im).rectangle(box, fill=(0, 0, 0, 0))
    return im


def symbol(name: Path, size: int) -> Image.Image:
    return load(name).resize((size, size), Image.LANCZOS)


def grey_goo(im: Image.Image, is_goo) -> Image.Image:
    """Pixels where is_goo(h, l, s) become grey goo (silver, by brightness)."""
    out = im.copy()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = im.getpixel((x, y))
            if not a:
                continue
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if is_goo(h, l, s):
                out.putpixel((x, y), tuple(int(d + (c - d) * l * 1.2) for d, c in zip(GOO_DARK, GOO_LIGHT)) + (a,))
    return out


def consensus(tier: int) -> Image.Image:
    im = clear(load(GAME / "gfx/interface/icons/buildings/brain_node_1.dds"), (50, 0, 77, 26))  # the flask
    im = grey_goo(im, lambda h, l, s: 0.0 < h < 0.22 and s > 0.25 and l < 0.75)  # the yellow undergrowth
    motes(im, (14, 66), (50, 0), 8 + 6 * tier, 40 + tier)
    unity = symbol(GAME / "gfx/interface/icons/resources/unity.dds", 20)
    halo = Image.new("RGBA", im.size)
    halo.alpha_composite(unity, (54, 4))
    im.alpha_composite(glow(halo, 1.0 + 0.6 * tier))
    im.alpha_composite(halo)
    draw = ImageDraw.Draw(im)
    for i in range(tier):  # tier pips
        x = 56 + i * 5
        draw.ellipse((x, 28, x + 3, 31), fill=SEAM + (255,))
    return im


def converter(tier: int) -> Image.Image:
    im = clear(load(GIGA / "gfx/interface/icons/buildings/building_giga_megaworkshop.dds"), (46, 0, 77, 26))
    if tier > 1:
        body = Image.new("RGBA", im.size)
        body.alpha_composite(im)
        im.alpha_composite(glow(body, 2.5))
        im.alpha_composite(body)
    nanites = symbol(GAME / "gfx/interface/icons/resources/nanites.dds", 15)
    tensile = symbol(GIGA / "gfx/interface/icons/resources/giga_sr_amb_megaconstruction.dds", 15)
    im.alpha_composite(nanites, (46, 3))
    im.alpha_composite(tensile, (61, 3))
    return im


def ancient_harvester() -> Image.Image:
    src = load(GAME / "gfx/interface/icons/modules/sb_nanite_harvester.dds")
    out = src.copy()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = src.getpixel((x, y))
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if s < 0.25 and l > 0.12:  # grey hull -> ancient bronze
                out.putpixel((x, y), (int(70 + 150 * l), int(48 + 105 * l), int(22 + 40 * l), a))
    lights = Image.new("RGBA", src.size)
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = src.getpixel((x, y))
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if b > r + 40 and g > r and l > 0.45 and s > 0.4:  # the module's bright blue lights
                lights.putpixel((x, y), SEAM + (a,))
    out.alpha_composite(glow(lights, 1.5))
    out.alpha_composite(lights)
    return out


if __name__ == "__main__":
    BUILDINGS.mkdir(parents=True, exist_ok=True)
    MODULES.mkdir(parents=True, exist_ok=True)
    for t in range(1, 5):
        consensus(t).save(BUILDINGS / f"lfg_nanite_consensus_{t}.dds")
    for t in (1, 2):
        converter(t).save(BUILDINGS / f"lfg_nanotensile_converter_{t}.dds")
    ancient_harvester().save(MODULES / "lfg_ancient_nanite_harvester.dds")
    print("wrote building icons")
