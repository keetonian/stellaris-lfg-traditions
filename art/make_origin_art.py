"""Builds the origins' art from vanilla files, in vanilla's origin style.

Nanite Forge:
- icon (40x40): a diamond in vanilla's origin-icon colours (sampled from Arc Welders' icon) with vanilla's nanite symbol
  (the Nanites resource icon) as the glyph;
- trait icon (29x29): a teal disc like vanilla's positive trait icons with the nanite symbol, for Nanite Substrate;
- picture (220x115, the origin picture size): a crop of vanilla's "gray gooed planet" event picture, a world engulfed
  by nanites.

Swallowed Whole (origin_lfg_sealed_ring):
- icon (40x40): the same diamond with a Tiyanki (the silhouette from vanilla's Tiyanki ship-category icon) rising out
  of a tilted ring world;
- picture (220x115): vanilla's ancient Tiyanki event picture looming over its ring world picture;
- Shadow Transactions perk (its Criminal Heritage perk, 52x60): vanilla's Universal Transactions icon (which Criminal
  Heritage can't take) gone crooked - its blue network turned blood red, the whole thing darker.

Needs Pillow (reads and writes .dds); not part of the stdlib-only tooling. Run from the repo root:
  python3 art/make_origin_art.py
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

GAME = Path.home() / "Library/Application Support/Steam/steamapps/common/Stellaris"
ICON_OUT = Path("mod/gfx/interface/icons/origins/lfg_origin_nanite_forge.dds")
SEALED_ICON_OUT = Path("mod/gfx/interface/icons/origins/lfg_origin_sealed_ring.dds")
SEALED_PICTURE_OUT = Path("mod/gfx/event_pictures/origins/lfg_origin_sealed_ring.dds")
SHADOW_PERK_OUT = Path("mod/gfx/interface/icons/ascension_perks/ap_lfg_shadow_transactions.dds")
TRAIT_OUT = Path("mod/gfx/interface/icons/traits/trait_lfg_nanite_substrate.dds")
PICTURE_OUT = Path("mod/gfx/event_pictures/origins/lfg_origin_nanite_forge.dds")
TOP, BOTTOM = (0, 112, 92), (0, 48, 41)  # diamond face, as sampled from vanilla's origin icons
GLYPH = (0, 225, 175)
RIM = (0, 213, 165)


def diamond_icon() -> Image.Image:
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
    return out.resize((w, w), Image.LANCZOS)


def stamp(out: Image.Image, mask: Image.Image, pos) -> None:
    """Draws a glyph mask onto an icon in the bright glyph colour, over a dark outline."""
    shadow = Image.new("RGBA", mask.size, (0, 20, 16, 255))
    shadow.putalpha(mask.filter(ImageFilter.MaxFilter(3)))
    bright = Image.new("RGBA", mask.size, GLYPH + (255,))
    bright.putalpha(mask)
    out.alpha_composite(shadow, pos)
    out.alpha_composite(bright, pos)


def icon() -> Image.Image:
    out = diamond_icon()
    glyph = Image.open(GAME / "gfx/interface/icons/resources/nanites_large.dds").convert("RGBA")
    size = 22
    stamp(out, glyph.getchannel("A").resize((size, size), Image.LANCZOS), ((40 - size) // 2, (40 - size) // 2))
    return out


def tiyanki_mask() -> Image.Image:
    """The Tiyanki silhouette of vanilla's ship-category icon (its first, teal, 50x50 disc): the glyph is the dark part
    of the disc, so its mask is how much darker than the disc each pixel is."""
    src = Image.open(GAME / "gfx/interface/icons/ship_categories/ship_category_tiyanki_rarity.dds").convert("RGBA")
    disc = src.crop((0, 0, 50, 50))
    mask = Image.new("L", disc.size)
    for y in range(50):
        for x in range(50):
            r, g, b, a = disc.getpixel((x, y))
            lum = (r + g + b) / 3
            mask.putpixel((x, y), int(max(0, min(255, (110 - lum) * 3.2))) if a > 200 else 0)
    return mask.crop((8, 13, 42, 44))  # the whale, without the little ship above it or the disc's rim


def sealed_ring_icon() -> Image.Image:
    """The diamond with a ring world (a tilted ellipse) and a Tiyanki rising out of it."""
    out = diamond_icon()
    scale = 4
    big = 40 * scale
    ring = Image.new("L", (big, big))
    ImageDraw.Draw(ring).ellipse((7 * scale, 23 * scale, 33 * scale, 32 * scale), outline=255, width=int(1.6 * scale))
    stamp(out, ring.resize((40, 40), Image.LANCZOS), (0, 0))
    whale = tiyanki_mask().resize((26, 24), Image.LANCZOS)
    stamp(out, whale, ((40 - 26) // 2, 6))
    return out


def sealed_ring_picture() -> Image.Image:
    """Vanilla's ring world event picture, with the ancient Tiyanki (lightened in: its background is near black)
    looming over it."""
    width = round(150 * 220 / 115)
    ring = Image.open(GAME / "gfx/event_pictures/ringworld.dds").convert("RGB")
    ring = ring.crop((450 - width, 0, 450, 150))
    whale = Image.open(GAME / "gfx/event_pictures/ancient_tiyanki.dds").convert("RGB")
    left = (450 - width) // 2
    whale = whale.crop((left, 0, left + width, 150))
    out = ImageChops.lighter(ImageEnhance.Brightness(ring).enhance(0.8), whale)
    return out.resize((220, 115), Image.LANCZOS).convert("RGBA")


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


def shadow_transactions_icon() -> Image.Image:
    """Universal Transactions with its cool (blue / teal) pixels turned red and everything darkened; the gold coins
    stay gold."""
    import colorsys
    src = Image.open(GAME / "gfx/interface/icons/ascension_perks/ap_universal_transactions.dds").convert("RGBA")
    out = src.copy()
    px = out.load()
    for y in range(src.size[1]):
        for x in range(src.size[0]):
            r, g, b, a = px[x, y]
            h, l, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if 0.4 < h < 0.75:  # cyan to blue
                h, sat = 0.99, min(1.0, sat * 1.3)
            l *= 0.8
            r, g, b = colorsys.hls_to_rgb(h, l, sat)
            px[x, y] = (int(r * 255), int(g * 255), int(b * 255), a)
    return out


for path, image in ((ICON_OUT, icon()), (TRAIT_OUT, trait_icon()), (PICTURE_OUT, picture()),
                    (SEALED_ICON_OUT, sealed_ring_icon()), (SEALED_PICTURE_OUT, sealed_ring_picture()),
                    (SHADOW_PERK_OUT, shadow_transactions_icon())):
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    print("wrote", path)
