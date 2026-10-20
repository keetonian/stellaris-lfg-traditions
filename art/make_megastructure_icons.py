"""Builds the Swarmforge's build-menu and tech icon (52x52, vanilla's tech-icon size): vanilla's Mega Shipyard tech icon
(tech_mega_shipyard) hue-shifted to the nanite cyan of art/make_component_icons.py, with the Nanites symbol and motes.
(The tech icon it replaces, tech_nanite_assemblers, carries a tier numeral.)

Needs Pillow; run from the repo root:
  python3 art/make_megastructure_icons.py
"""
from pathlib import Path
from PIL import Image

from make_component_icons import GAME, SEAM, glyph, motes

OUT = Path("mod/gfx/interface/icons/megastructures/lfg_swarmforge.dds")
TECH_OUT = Path("mod/gfx/interface/icons/technologies/tech_lfg_swarmforge.dds")  # its tech uses the same art
PULSE_OUT = Path("mod/gfx/interface/icons/decisions/decision_lfg_nanite_pulse.dds")  # the Nanite Pulse decision


def cyan(src: Image.Image) -> Image.Image:
    out = Image.new("RGBA", src.size)
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = src.getpixel((x, y))
            v = max(r, g, b) / 255
            out.putpixel((x, y), (int(SEAM[0] * v * 1.1), int(SEAM[1] * v * 1.1), int(SEAM[2] * v * 1.1), a))
    return out


def pulse() -> Image.Image:
    """The Nanite Pulse decision: vanilla's pulsar decision icon in nanite cyan, with the Nanites symbol."""
    src = Image.open(GAME / "gfx/interface/icons/decisions/decision_star_pulsar.dds").convert("RGBA")
    out = cyan(src)
    size = src.width * 2 // 5
    glyph(out, size, ((src.width - size) // 2, (src.height - size) // 2))
    return out


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
    icon = swarmforge()
    for out in (OUT, TECH_OUT):
        out.parent.mkdir(parents=True, exist_ok=True)
        icon.save(out)
        print(f"wrote {out}")
    PULSE_OUT.parent.mkdir(parents=True, exist_ok=True)
    pulse().save(PULSE_OUT)
    print(f"wrote {PULSE_OUT}")
