"""Draws the mod's own symbols (no vanilla icons reused), at 8x and scaled down:

- Megaforge and Stationcraft trees: the five tradition icons (45x45: the symbol on a lit gradient square, ember tones for
  Megaforge, violet for Stationcraft) and the tree icon (30x30: a silver symbol, like vanilla's tree icons);
- council agendas (124x124: a mint line symbol on transparency, about 54 px across and centred, like vanilla's agenda icons);
- the Progenitor Forge's tech and build-menu icon (52x52: an O-class star in two nanite rings).

Needs Pillow; run from the repo root:
  python3 art/make_glyph_icons.py
"""
from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

S = 360  # drawing canvas (a 45 px icon at 8x)
TRADITIONS = Path("mod/gfx/interface/icons/traditions")
AGENDAS = Path("mod/gfx/interface/icons/agenda_icons")
MINT = (130, 245, 205)
SILVER = (205, 220, 225)


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("L", (S, S), 0)
    return im, ImageDraw.Draw(im)


def ring(d, cx, cy, rx, ry, w):
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=255, width=w)


def disc(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)


def poly(d, pts, fill=True, w=14):
    if fill:
        d.polygon(pts, fill=255)
    else:
        d.line(pts + [pts[0]], fill=255, width=w, joint="curve")


def line(d, pts, w=16):
    d.line(pts, fill=255, width=w, joint="curve")


def star(d, cx, cy, r, points=4, inner=0.35):
    pts = []
    for i in range(points * 2):
        a = math.pi * i / points - math.pi / 2
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=255)


def hexagon(cx, cy, r, rot=0):
    return [(cx + r * math.cos(math.radians(60 * i + rot)), cy + r * math.sin(math.radians(60 * i + rot))) for i in range(6)]


def station(d, cx, cy, r):
    """A starbase: hub, ring, four arms."""
    ring(d, cx, cy, r, r, int(r * 0.16))
    disc(d, cx, cy, r * 0.38)
    for a in range(0, 360, 90):
        x, y = cx + r * 1.25 * math.cos(math.radians(a + 45)), cy + r * 1.25 * math.sin(math.radians(a + 45))
        line(d, [(cx, cy), (x, y)], int(r * 0.14))
        disc(d, x, y, r * 0.16)


# ---- symbols (each draws on an S x S mask) ----

def sym_megaforge_ring(d):  # a star inside a ring megastructure of twelve plates
    star(d, 180, 180, 70, 4, 0.3)
    disc(d, 180, 180, 30)
    for k in range(12):
        a0, a1 = 30 * k + 4, 30 * k + 26
        d.arc((40, 40, 320, 320), a0, a1, fill=255, width=34)


def sym_guilds(d):  # crossed hammer and girder
    line(d, [(80, 280), (270, 90)], 26)
    d.rectangle((230, 50, 320, 120), fill=255)  # hammer head (rotated look)
    line(d, [(90, 90), (280, 280)], 40)
    for i in range(5):  # girder holes
        t = 0.15 + i * 0.17
        x, y = 90 + 190 * t, 90 + 190 * t
        disc_hole = (x - 9, y - 9, x + 9, y + 9)
        d.ellipse(disc_hole, fill=0)


def sym_lattices(d):  # a supertensile lattice
    for cx, cy in ((180, 180), (180, 80), (180, 280), (93, 130), (267, 130), (93, 230), (267, 230)):
        poly(d, hexagon(cx, cy, 52, 30), fill=False, w=14)


def sym_priority(d):  # a chevron pointing up under a star
    poly(d, [(60, 300), (180, 180), (300, 300), (300, 250), (180, 130), (60, 250)])
    star(d, 180, 80, 62)


def sym_foundries(d):  # a crucible pouring
    poly(d, [(70, 120), (250, 120), (230, 270), (90, 270)])
    d.polygon([(250, 120), (300, 100), (290, 140)], fill=255)
    line(d, [(295, 150), (300, 250)], 18)
    disc(d, 300, 290, 26)


def sym_monuments(d):  # a tall monument spire with rings
    poly(d, [(180, 40), (220, 300), (140, 300)])
    ring(d, 180, 200, 110, 30, 16)
    ring(d, 180, 130, 80, 22, 14)
    d.rectangle((100, 300, 260, 330), fill=255)


def sym_stationcraft(d):  # a starbase
    station(d, 180, 180, 95)


def sym_logistics(d):  # a starbase with supply arrows around it
    station(d, 180, 180, 70)
    d.arc((40, 40, 320, 320), 200, 330, fill=255, width=18)
    d.arc((40, 40, 320, 320), 20, 150, fill=255, width=18)
    d.polygon([(306, 116), (330, 170), (276, 160)], fill=255)
    d.polygon([(54, 244), (30, 190), (84, 200)], fill=255)


def sym_kilostructure(d):  # a blueprint: grid with a half-built ring
    for x in range(60, 310, 50):
        d.line([(x, 50), (x, 310)], fill=110, width=6)
        d.line([(50, x), (310, x)], fill=110, width=6)
    d.arc((70, 70, 290, 290), 160, 380, fill=255, width=28)
    disc(d, 180, 180, 40)


def sym_bastion(d):  # a shield over a starbase
    poly(d, [(180, 40), (310, 90), (290, 230), (180, 320), (70, 230), (50, 90)], fill=False, w=22)
    station(d, 180, 175, 55)


def sym_self_repair(d):  # a wrench across a frame
    poly(d, hexagon(180, 180, 130, 0), fill=False, w=20)
    line(d, [(110, 250), (240, 120)], 34)
    disc(d, 255, 105, 46)
    d.ellipse((240, 70, 290, 120), fill=0)  # wrench jaw
    disc(d, 105, 255, 26)


def sym_refineries(d):  # a starbase drawing a stream from an asteroid
    station(d, 230, 140, 60)
    poly(d, [(40, 260), (90, 220), (150, 240), (160, 300), (100, 330), (50, 310)])
    for i in range(5):
        t = i / 4
        disc(d, 140 + 70 * t, 240 - 70 * t, 14 - 6 * t)


def sym_expedition(d):  # a dig: trowel over a broken pillar
    d.rectangle((90, 170, 160, 320), fill=255)
    poly(d, [(90, 170), (160, 170), (140, 140), (110, 150)])
    poly(d, [(200, 300), (300, 200), (330, 260), (260, 330)])
    line(d, [(250, 250), (190, 110)], 18)
    disc(d, 185, 100, 22)


def sym_tithe(d):  # a sheaf of wheat
    for dx in (-60, 0, 60):
        line(d, [(180 + dx * 0.4, 320), (180 + dx, 90)], 14)
        for k in range(4):
            y = 110 + k * 40
            x = 180 + dx * (1 - (y - 90) / 230 * 0.6)
            d.ellipse((x - 26, y - 16, x - 2, y + 16), fill=255)
            d.ellipse((x + 2, y - 16, x + 26, y + 16), fill=255)
    d.rectangle((120, 230, 240, 250), fill=255)


def sym_gala(d):  # a spotlight beam on a star
    poly(d, [(60, 320), (120, 300), (260, 80), (300, 110)])
    star(d, 270, 80, 70, 5, 0.45)


def sym_grand_tour(d):  # a planet with a liner's orbit
    disc(d, 180, 190, 80)
    ring(d, 180, 190, 160, 60, 14)
    d.rectangle((20, 182, 340, 196), fill=0)
    disc(d, 180, 190, 80)
    poly(d, [(300, 120), (340, 140), (300, 160)])


def sym_feast(d):  # a cornucopia overflowing
    poly(d, [(60, 120), (150, 140), (260, 220), (290, 300), (230, 260), (130, 190)])
    for x, y, r in ((270, 180, 30), (310, 230, 26), (240, 140, 24), (320, 170, 18)):
        disc(d, x, y, r)


def sym_progenitor(d):  # an O-class star inside two tilted nanite rings, swarm motes around
    for tilt in (-30, 30):
        box = Image.new("L", (S, S), 0)
        bd = ImageDraw.Draw(box)
        for k in range(16):
            bd.arc((20, 135, 340, 225), 22.5 * k + 4, 22.5 * k + 18, fill=255, width=12)
        box = box.rotate(tilt, resample=Image.BICUBIC, center=(180, 180))
        d.bitmap((0, 0), box, fill=255)
    d.ellipse((115, 115, 245, 245), fill=0)  # dark gap around the star
    star(d, 180, 180, 78, 8, 0.32)
    disc(d, 180, 180, 40)
    for x, y, r in ((60, 70, 10), (300, 60, 8), (310, 290, 11), (50, 300, 9), (180, 30, 7), (330, 180, 7), (30, 180, 8)):
        disc(d, x, y, r)


# ---- renderers ----

def tradition(sym, top, bottom, accent, size=45) -> Image.Image:
    """The symbol, lit, on a gradient square with a vignette."""
    big = S
    bg = Image.new("RGB", (big, big))
    px = bg.load()
    for y in range(big):
        for x in range(big):
            t = y / big
            dx, dy = (x - big * 0.55) / big, (y - big * 0.35) / big
            v = max(0.0, 1 - math.hypot(dx, dy) * 1.6)  # light from the upper right
            px[x, y] = tuple(int(a + (b - a) * t + 70 * v) for a, b in zip(top, bottom))
    mask, d = canvas()
    sym(d)
    glow = Image.new("RGB", (big, big), accent)
    halo = mask.filter(ImageFilter.GaussianBlur(14))
    out = Image.composite(glow, bg, halo.point(lambda v: int(v * 0.7)))
    light = Image.new("RGB", (big, big))
    lp = light.load()
    for y in range(big):  # bright at the top, the accent below
        for x in range(big):
            t = y / big
            lp[x, y] = tuple(int(255 + (a - 255) * t) for a in accent)
    out = Image.composite(light, out, mask)
    out = out.resize((size, size), Image.LANCZOS).convert("RGBA")
    return out


def glyph(sym, colour, size) -> Image.Image:
    mask, d = canvas()
    sym(d)
    mask = mask.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), colour + (0,))
    out.putalpha(mask)
    return out


AGENDA_SIZE = 124
AGENDA_BOX = 54  # vanilla agenda symbols span ~40-58 px of the 124 px icon, centred


def agenda(sym) -> Image.Image:
    """A council agenda icon: the symbol cropped to its ink, fitted into AGENDA_BOX and centred, in mint."""
    mask, d = canvas()
    sym(d)
    mask = mask.crop(mask.getbbox())
    k = AGENDA_BOX / max(mask.size)
    mask = mask.resize((max(1, round(mask.width * k)), max(1, round(mask.height * k))), Image.LANCZOS)
    full = Image.new("L", (AGENDA_SIZE, AGENDA_SIZE), 0)
    full.paste(mask, ((AGENDA_SIZE - mask.width) // 2, (AGENDA_SIZE - mask.height) // 2))
    out = Image.new("RGBA", full.size, MINT + (0,))
    out.putalpha(full)
    return out


MEGAFORGE = ((70, 22, 8), (25, 8, 4), (255, 150, 60))
PROGENITOR = ((10, 30, 70), (2, 6, 20), (90, 200, 255))
STATIONCRAFT = ((40, 20, 70), (12, 8, 30), (180, 140, 255))

ICONS = {
    TRADITIONS / "tradition_lfg_megaforge_guilds.dds": lambda: tradition(sym_guilds, *MEGAFORGE),
    TRADITIONS / "tradition_lfg_megaforge_lattices.dds": lambda: tradition(sym_lattices, *MEGAFORGE),
    TRADITIONS / "tradition_lfg_megaforge_priority.dds": lambda: tradition(sym_priority, *MEGAFORGE),
    TRADITIONS / "tradition_lfg_megaforge_foundries.dds": lambda: tradition(sym_foundries, *MEGAFORGE),
    TRADITIONS / "tradition_lfg_megaforge_monuments.dds": lambda: tradition(sym_monuments, *MEGAFORGE),
    TRADITIONS / "tree_icons/tradition_icon_lfg_megaforge.dds": lambda: glyph(sym_megaforge_ring, SILVER, 30),
    TRADITIONS / "tradition_lfg_stationcraft_orbital_logistics.dds": lambda: tradition(sym_logistics, *STATIONCRAFT),
    TRADITIONS / "tradition_lfg_stationcraft_kilostructure_doctrine.dds": lambda: tradition(sym_kilostructure, *STATIONCRAFT),
    TRADITIONS / "tradition_lfg_stationcraft_bastion_starbases.dds": lambda: tradition(sym_bastion, *STATIONCRAFT),
    TRADITIONS / "tradition_lfg_stationcraft_self_repairing_frames.dds": lambda: tradition(sym_self_repair, *STATIONCRAFT),
    TRADITIONS / "tradition_lfg_stationcraft_orbital_refineries.dds": lambda: tradition(sym_refineries, *STATIONCRAFT),
    TRADITIONS / "tree_icons/tradition_icon_lfg_stationcraft.dds": lambda: glyph(sym_stationcraft, SILVER, 30),
    Path("mod/gfx/interface/icons/technologies/tech_lfg_progenitor_forge.dds"): lambda: tradition(sym_progenitor, *PROGENITOR, size=52),
    Path("mod/gfx/interface/icons/megastructures/lfg_progenitor_forge.dds"): lambda: tradition(sym_progenitor, *PROGENITOR, size=52),
    AGENDAS / "agenda_lfg_great_project.dds": lambda: agenda(sym_megaforge_ring),
    AGENDAS / "agenda_lfg_grand_expedition.dds": lambda: agenda(sym_expedition),
    AGENDAS / "agenda_lfg_harvest_tithe.dds": lambda: agenda(sym_tithe),
    AGENDAS / "agenda_lfg_gala_season.dds": lambda: agenda(sym_gala),
    AGENDAS / "agenda_lfg_grand_tour_season.dds": lambda: agenda(sym_grand_tour),
    AGENDAS / "agenda_lfg_feast_of_plenty.dds": lambda: agenda(sym_feast),
}

if __name__ == "__main__":
    for path, make in ICONS.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        make().save(path)
    print(f"wrote {len(ICONS)} icons")
