"""Builds the Nanite Forge origin's art from vanilla files, in vanilla's origin style:

- icon (40x40): a diamond in vanilla's origin-icon colours (sampled from Arc Welders' icon) with vanilla's nanite symbol
  (the Nanites resource icon) as the glyph;
- trait icon (29x29): a teal disc like vanilla's positive trait icons with the nanite symbol, for Nanite Substrate;
- picture (220x115, the origin picture size): a crop of vanilla's "gray gooed planet" event picture, a world engulfed
  by nanites.

Needs Pillow (reads and writes .dds); not part of the stdlib-only tooling. Run from the repo root:
  python3 art/make_origin_art.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

GAME = Path.home() / "Library/Application Support/Steam/steamapps/common/Stellaris"
ICON_OUT = Path("mod/gfx/interface/icons/origins/lfg_origin_nanite_forge.dds")
TRAIT_OUT = Path("mod/gfx/interface/icons/traits/trait_lfg_nanite_substrate.dds")
PICTURE_OUT = Path("mod/gfx/event_pictures/origins/lfg_origin_nanite_forge.dds")
TOP, BOTTOM = (0, 112, 92), (0, 48, 41)  # diamond face, as sampled from vanilla's origin icons
GLYPH = (0, 225, 175)
RIM = (0, 213, 165)


def icon() -> Image.Image:
    """A diamond like vanilla's origin icons (bright rim, teal face darkening downwards), drawn at 4x and scaled down."""
    scale, w = 4, 40
    big = w * scale
    face = Image.new("RGBA", (big, big))
    for y in range(big):
        t = y / (big - 1)
        colour = tuple(int(a + (b - a) * t) for a, b in zip(TOP, BOTTOM)) + (255,)
        for x in range(big):
            face.putpixel((x, y), colour)
    def diamond(inset: int) -> Image.Image:
        m = Image.new("L", (big, big))
        c, r = big / 2, big / 2 - inset
        ImageDraw.Draw(m).polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], fill=255)
        return m
    out = Image.new("RGBA", (big, big))
    out.paste(Image.new("RGBA", (big, big), RIM + (255,)), mask=diamond(1 * scale))
    out.paste(face, mask=diamond(3 * scale))
    out = out.resize((w, w), Image.LANCZOS)
    glyph = Image.open(GAME / "gfx/interface/icons/resources/nanites_large.dds").convert("RGBA")
    size = 22
    mask = glyph.getchannel("A").resize((size, size), Image.LANCZOS)
    shadow = Image.new("RGBA", (size, size), (0, 20, 16, 255))
    shadow.putalpha(mask.filter(ImageFilter.MaxFilter(3)))
    bright = Image.new("RGBA", (size, size), GLYPH + (255,))
    bright.putalpha(mask)
    pos = ((w - size) // 2, (w - size) // 2)
    out.alpha_composite(shadow, pos)
    out.alpha_composite(bright, pos)
    return out


def trait_icon() -> Image.Image:
    """The Nanite Substrate trait: a teal disc like vanilla's positive trait icons (29x29) with the nanite symbol, dark."""
    scale, w = 4, 29
    big = w * scale
    disc = Image.new("RGBA", (big, big))
    for y in range(big):
        t = y / (big - 1)
        colour = tuple(int(a + (b - a) * t) for a, b in zip((0, 194, 150), (3, 139, 107))) + (255,)
        for x in range(big):
            disc.putpixel((x, y), colour)
    mask = Image.new("L", (big, big))
    ImageDraw.Draw(mask).ellipse((scale, scale, big - scale, big - scale), fill=255)
    out = Image.new("RGBA", (big, big))
    out.paste(disc, mask=mask)
    out = out.resize((w, w), Image.LANCZOS)
    glyph = Image.open(GAME / "gfx/interface/icons/resources/nanites_large.dds").convert("RGBA")
    size = 19
    dark = Image.new("RGBA", (size, size), (17, 28, 25, 255))
    dark.putalpha(glyph.getchannel("A").resize((size, size), Image.LANCZOS))
    out.alpha_composite(dark, ((w - size) // 2, (w - size) // 2))
    return out


def picture() -> Image.Image:
    src = Image.open(GAME / "gfx/event_pictures/gray_gooed_planet.dds").convert("RGBA")
    width = round(src.size[1] * 220 / 115)  # widest crop with the origin picture's aspect, centred on the planet
    left = (src.size[0] - width) // 2
    return src.crop((left, 0, left + width, src.size[1])).resize((220, 115), Image.LANCZOS)


for path, image in ((ICON_OUT, icon()), (TRAIT_OUT, trait_icon()), (PICTURE_OUT, picture())):
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    print("wrote", path)
