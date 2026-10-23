"""Tempest tradition tree art (our own drawings, in the style of make_glyph_icons.py):

- the five tradition icons (45x45, electric blue), the tree icon (30x30, silver) and the Storm Season agenda icon
  (124x124, mint, like the other agenda icons);
- the tree's background tile and hex strip: vanilla's Synchronicity ones tinted storm blue (make_megastructure_icons.tint);
- the vortex layout's arrows (interface/lfg_tradition_trees.gui, tree_lfg_vortex): four curved arrows running clockwise
  around the ring of tradition slots (1 -> 2 -> 3 -> 4 -> 5), in vanilla's arrow teal, and a faint spiral in the eye.

Needs Pillow; run from the repo root:
  python3 art/make_tempest_art.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from make_glyph_icons import AGENDAS, SILVER, TRADITIONS, agenda, disc, glyph, line, ring, tradition  # noqa: E402
from make_megastructure_icons import GAME, tint  # noqa: E402

TEMPEST = ((14, 30, 70), (4, 8, 26), (120, 220, 255))
ARROWS = Path("mod/gfx/interface/traditions/lfg_vortex_arrows.dds")

# The vortex layout, as in interface/lfg_tradition_trees.gui: 44 px slots at these top-left corners (tree coordinates),
# and the arrow image placed at ARROW_ORIGIN.
SLOT = 44
SLOTS = [(131, 53), (199, 103), (173, 183), (89, 183), (62, 103)]
ARROW_ORIGIN = (55, 45)
ARROW_SIZE = (200, 190)
TEAL = (63, 120, 105)


def bolt(d, x, y, h, w=None):
    """A lightning bolt, top at (x, y), h tall."""
    w = w or h * 0.45
    pts = [(x + w * 0.15, y), (x - w * 0.45, y + h * 0.55), (x - w * 0.02, y + h * 0.55),
           (x - w * 0.2, y + h), (x + w * 0.5, y + h * 0.38), (x + w * 0.05, y + h * 0.38), (x + w * 0.35, y)]
    d.polygon(pts, fill=255)


def spiral(d, cx, cy, r0, r1, turns, w, start=0.0):
    pts = []
    n = int(120 * turns)
    for i in range(n + 1):
        t = i / n
        a = start + 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    line(d, pts, w)


# ---- symbols (S x S = 360 masks) ----

def sym_tempest(d):  # a vortex with a bolt through its eye
    spiral(d, 180, 180, 30, 150, 1.6, 26)
    bolt(d, 185, 95, 170)


def sym_storm_logs(d):  # a logbook page ruled with storm tracks
    d.rounded_rectangle((80, 50, 280, 310), radius=18, outline=255, width=20)
    for i, y in enumerate((110, 160, 210, 260)):
        line(d, [(115, y), (165, y - 18), (205, y + 10), (245, y - 12)], 14)
    disc(d, 255, 85, 16)


def sym_eye_walkers(d):  # an eye in the middle of a swirling storm
    spiral(d, 180, 180, 95, 160, 0.85, 20, start=math.pi)
    d.ellipse((95, 135, 265, 225), outline=255, width=18)
    disc(d, 180, 180, 30)


def sym_storm_harvest(d):  # a lightning rod tower drinking a bolt
    line(d, [(180, 330), (180, 150)], 22)
    line(d, [(120, 330), (180, 230), (240, 330)], 16)
    line(d, [(140, 270), (220, 270)], 14)
    disc(d, 180, 145, 18)
    bolt(d, 165, 20, 120, 70)


def sym_lightning_rods(d):  # two arrows bending a storm's path around a star
    disc(d, 180, 180, 26)
    for a0 in (200, 20):
        d.arc((70, 70, 290, 290), a0, a0 + 120, fill=255, width=22)
        a = math.radians(a0 + 120)
        x, y = 180 + 110 * math.cos(a), 180 + 110 * math.sin(a)
        t = (-math.sin(a), math.cos(a))
        n = (math.cos(a), math.sin(a))
        d.polygon([(x + t[0] * 40, y + t[1] * 40), (x + n[0] * 30, y + n[1] * 30), (x - n[0] * 30, y - n[1] * 30)], fill=255)


def sym_ride_lightning(d):  # a ship's chevron riding a bolt
    bolt(d, 230, 30, 300, 150)
    d.polygon([(70, 250), (150, 130), (180, 160), (120, 270)], fill=255)
    d.polygon([(70, 250), (120, 270), (95, 300)], fill=255)


# ---- the vortex arrows ----

def vortex_arrows() -> Image.Image:
    k = 4  # drawn at 4x, scaled down
    w, h = ARROW_SIZE[0] * k, ARROW_SIZE[1] * k
    im = Image.new("RGBA", (w, h), TEAL + (0,))
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    centres = [((x + SLOT / 2 - ARROW_ORIGIN[0]) * k, (y + SLOT / 2 - ARROW_ORIGIN[1]) * k) for x, y in SLOTS]
    cx = sum(c[0] for c in centres) / len(centres)
    cy = sum(c[1] for c in centres) / len(centres)
    r = sum(math.hypot(x - cx, y - cy) for x, y in centres) / len(centres)
    angles = [math.atan2(y - cy, x - cx) for x, y in centres]
    trim = (SLOT * 0.62 * k) / r  # leave the slots clear
    for i in range(4):  # 1 -> 2, 2 -> 3, 3 -> 4, 4 -> 5 (clockwise on screen)
        a0, a1 = angles[i], angles[i + 1]
        if a1 < a0:
            a1 += 2 * math.pi
        a0 += trim
        a1 -= trim
        pts = [(cx + r * math.cos(a0 + (a1 - a0) * t / 40), cy + r * math.sin(a0 + (a1 - a0) * t / 40)) for t in range(41)]
        d.line(pts[:-4], fill=235, width=5 * k, joint="curve")
        # arrowhead along the tangent at the end
        ex, ey = pts[-1]
        tx, ty = -math.sin(a1), math.cos(a1)
        nx, ny = math.cos(a1), math.sin(a1)
        hl, hw = 11 * k, 7 * k
        d.polygon([(ex, ey), (ex - tx * hl + nx * hw, ey - ty * hl + ny * hw), (ex - tx * hl - nx * hw, ey - ty * hl - ny * hw)],
                  fill=235)
    # a faint spiral in the eye
    eye = Image.new("L", (w, h), 0)
    spiral(ImageDraw.Draw(eye), cx, cy, 4 * k, r * 0.42, 1.4, 3 * k, start=-math.pi / 2)
    mask = Image.composite(mask, eye.point(lambda v: v * 90 // 255), mask)
    im.putalpha(mask)
    return im.resize(ARROW_SIZE, Image.LANCZOS)


STORM_BLUE = (90, 170, 255)

ICONS = {
    TRADITIONS / "tradition_lfg_tempest_storm_logs.dds": lambda: tradition(sym_storm_logs, *TEMPEST),
    TRADITIONS / "tradition_lfg_tempest_eye_walkers.dds": lambda: tradition(sym_eye_walkers, *TEMPEST),
    TRADITIONS / "tradition_lfg_tempest_storm_harvest.dds": lambda: tradition(sym_storm_harvest, *TEMPEST),
    TRADITIONS / "tradition_lfg_tempest_lightning_rods.dds": lambda: tradition(sym_lightning_rods, *TEMPEST),
    TRADITIONS / "tradition_lfg_tempest_ride_the_lightning.dds": lambda: tradition(sym_ride_lightning, *TEMPEST),
    TRADITIONS / "tree_icons/tradition_icon_lfg_tempest.dds": lambda: glyph(sym_tempest, SILVER, 30),
    ARROWS: vortex_arrows,
    AGENDAS / "agenda_lfg_storm_season.dds": lambda: agenda(sym_tempest),
    Path("mod/gfx/interface/tiles/tradition_category_tile_lfg_tempest.dds"): lambda: tint(
        Image.open(GAME / "gfx/interface/tiles/tradition_category_tile_synchronicity.dds").convert("RGBA"), STORM_BLUE),
    Path("mod/gfx/interface/traditions/tradition_hex_bg_lfg_tempest.dds"): lambda: tint(
        Image.open(GAME / "gfx/interface/traditions/tradition_hex_bg_synchronicity.dds").convert("RGBA"), STORM_BLUE),
}

if __name__ == "__main__":
    for path, make in ICONS.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        make().save(path)
    print(f"wrote {len(ICONS)} images")
