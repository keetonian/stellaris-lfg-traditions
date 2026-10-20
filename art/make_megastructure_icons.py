"""Builds the Swarmforge's build-menu icon (52x52, vanilla's tech-icon size): vanilla's Mega Shipyard tech icon
(tech_mega_shipyard) hue-shifted to the nanite cyan of art/make_component_icons.py, with the Nanites symbol and motes.
(The tech icon it replaces, tech_nanite_assemblers, carries a tier numeral.)

Needs Pillow; run from the repo root:
  python3 art/make_megastructure_icons.py
"""
from pathlib import Path
from PIL import Image

from make_component_icons import GAME, SEAM, glyph, motes

OUT = Path("mod/gfx/interface/icons/megastructures/lfg_swarmforge.dds")


def swarmforge() -> Image.Image:
    src = Image.open(GAME / "gfx/interface/icons/technologies/tech_mega_shipyard.dds").convert("RGBA")
    # Hue shift: every pixel becomes nanite cyan at its own brightness, so the dark starfield stays dark.
    out = Image.new("RGBA", src.size)
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = src.getpixel((x, y))
            v = max(r, g, b) / 255
            out.putpixel((x, y), (int(SEAM[0] * v * 1.1), int(SEAM[1] * v * 1.1), int(SEAM[2] * v * 1.1), a))
    glyph(out, 14, (19, 18))  # in the shipyard's ring
    motes(out, (34, 34), (12, 12), 12, 31)
    return out


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    swarmforge().save(OUT)
    print(f"wrote {OUT}")
