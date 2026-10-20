"""Builds the Mothership components' icons (58x58, vanilla's ship-part icon size) from vanilla icons, in one nanite
style (dark gunmetal with glowing cyan, the Nanites resource symbol, drifting nanite motes):

- Nanite Armour: vanilla's top armour plate (ship_part_armor_5) without its tier numeral "V";
- Nanite Swarm Hangar: vanilla's fighter (ship_part_strike_craft_fighter_3) without its "III", as a swarm of three;
- Nanite Reshaper: vanilla's Reshaping Projectile Accelerator (ship_part_lm_accelerator), its living metal recoloured;
- Nanite Siege Driver: vanilla's Giga Cannon (ship_part_mass_accelerator_2, the X-slot kinetic) with the nanite symbol;
- Nanite Flak Swarm: vanilla's point defence (ship_part_point_defense_3) without its "III", throwing out a cloud of motes;
- Nanite Disassembler: vanilla's World Cracker (ship_part_world_cracker), its fiery beam turned into a nanite stream;
- Nanite Storm Autocannon: vanilla's Nanite Autocannon (ship_part_autocannon_4) without its "IV", recoloured;
- swarm modules: the fighter (swarmers) or bomber (interdictors) in nanite colours, with a hexagonal frame (vaults:
  storage) or the nanite symbol and motes (foundries: assembly).

Needs Pillow (reads and writes .dds); not part of the stdlib-only tooling. Run from the repo root:
  python3 art/make_component_icons.py
"""
from __future__ import annotations

import colorsys
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

GAME = Path.home() / "Library/Application Support/Steam/steamapps/common/Stellaris"
PARTS = GAME / "gfx/interface/icons/ship_parts"
OUT = Path("mod/gfx/interface/icons/ship_parts")
METAL_DARK, METAL_LIGHT = (24, 30, 36), (150, 165, 175)  # gunmetal shading
SEAM = (60, 200, 220)  # glowing nanite cyan
GLYPH = (170, 240, 245)


def source(name: str, cut: tuple[int, int] | None = None) -> Image.Image:
    """A vanilla ship-part icon; `cut` = (x, y): clear everything right of x and below y (its tier numeral)."""
    im = Image.open(PARTS / f"ship_part_{name}.dds").convert("RGBA")
    if cut:
        ImageDraw.Draw(im).rectangle((cut[0], cut[1], im.width, im.height), fill=(0, 0, 0, 0))
    return im


def nanite_metal(im: Image.Image, glow_of) -> Image.Image:
    """Recolour: brightness -> gunmetal, and `glow_of(r, g, b)` (0-1) of each pixel -> nanite cyan."""
    out = Image.new("RGBA", im.size)
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = im.getpixel((x, y))
            if a == 0:
                continue
            lum = (r + g + b) / 765
            base = tuple(int(d + (l - d) * lum) for d, l in zip(METAL_DARK, METAL_LIGHT))
            k = min(1.0, glow_of(r, g, b))
            out.putpixel((x, y), tuple(int(c + (s - c) * k) for c, s in zip(base, SEAM)) + (a,))
    return out


def cyan_seams(r: int, g: int, b: int) -> float:
    return max(0.0, (g + b) / 2 - r) / 255 * 1.1  # vanilla's glowing parts are the green-blue pixels


def warm_parts(r: int, g: int, b: int) -> float:
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return s * (1.2 if l > 0.15 else 0.6) if h < 0.17 or h > 0.9 else 0.0  # living metal's reds, oranges, golds


def glow(layer: Image.Image, radius: float) -> Image.Image:
    halo = Image.new("RGBA", layer.size, SEAM + (0,))
    halo.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius)))
    return halo


def glyph(out: Image.Image, size: int, pos: tuple[int, int]) -> None:
    """The Nanites resource symbol, softly glowing."""
    mask = Image.open(GAME / "gfx/interface/icons/resources/nanites_large.dds").getchannel("A")
    mask = mask.resize((size, size), Image.LANCZOS).point(lambda v: v * 0.85)
    layer = Image.new("RGBA", out.size)
    bright = Image.new("RGBA", (size, size), GLYPH + (255,))
    bright.putalpha(mask)
    layer.alpha_composite(bright, pos)
    out.alpha_composite(glow(layer, 1.2))
    out.alpha_composite(layer)


def motes(out: Image.Image, start: tuple[float, float], step: tuple[float, float], count: int, seed: int) -> None:
    """Nanite motes drifting from `start` along `step`, shrinking and fading."""
    layer = Image.new("RGBA", out.size)
    draw = ImageDraw.Draw(layer)
    rng = random.Random(seed)
    for _ in range(count):
        t = rng.random()
        x = start[0] + t * step[0] + rng.uniform(-3, 3)
        y = start[1] + t * step[1] + rng.uniform(-3, 3)
        r = 1.0 - t * 0.5
        draw.ellipse((x - r, y - r, x + r, y + r), fill=SEAM + (int(230 * (1 - t * 0.7)),))
    out.alpha_composite(layer)


def armour() -> Image.Image:
    out = nanite_metal(source("armor_5", cut=(37, 39)), cyan_seams)  # "V": right of x=37, below y=39
    glyph(out, 18, (17, 16))
    motes(out, (41, 36), (13, 17), 14, 7)  # off the corner where the numeral was
    return out


def hangar() -> Image.Image:
    craft = nanite_metal(source("strike_craft_fighter_3", cut=(37, 41)), cyan_seams)  # "III": right of 37, below 41
    out = Image.new("RGBA", craft.size)
    for scale, pos in ((0.42, (32, 2)), (0.42, (30, 32)), (0.68, (2, 12))):  # a swarm: two escorts, the lead in front
        w = int(craft.width * scale)
        out.alpha_composite(craft.resize((w, w), Image.LANCZOS), pos)
    motes(out, (44, 30), (10, 22), 12, 11)
    return out


def reshaper() -> Image.Image:
    out = nanite_metal(source("lm_accelerator"), warm_parts)
    glyph(out, 14, (37, 38))  # on the canister
    motes(out, (14, 26), (-12, 8), 12, 5)  # from the muzzle
    return out


def siege_driver() -> Image.Image:
    im = source("mass_accelerator_2", cut=(41, 36))  # "II": right of 41, below 36
    out = nanite_metal(im, lambda r, g, b: max(cyan_seams(r, g, b), warm_parts(r, g, b)))
    glyph(out, 16, (21, 21))
    motes(out, (12, 14), (-10, -10), 12, 3)
    return out


def flak_swarm() -> Image.Image:
    out = nanite_metal(source("point_defense_3", cut=(38, 40)), cyan_seams)  # "III": right of 38, below 40
    motes(out, (14, 14), (-12, -10), 18, 9)  # from the barrels
    motes(out, (20, 8), (4, -8), 10, 13)
    return out


def disassembler() -> Image.Image:
    out = nanite_metal(source("world_cracker"), lambda r, g, b: warm_parts(r, g, b) * 1.3)
    motes(out, (14, 44), (34, -34), 22, 17)  # along the beam
    glyph(out, 16, (6, 36))  # on the shattering world
    return out


def storm_autocannon() -> Image.Image:
    out = nanite_metal(source("autocannon_4", cut=(35, 37)), lambda r, g, b: max(cyan_seams(r, g, b), warm_parts(r, g, b)))
    glyph(out, 14, (38, 40))
    motes(out, (8, 26), (-8, 6), 12, 23)  # from the muzzle
    return out


def craft(name: str) -> Image.Image:
    """A strike craft icon without its "III" (right of x=37, below y=41), scaled down to leave room for an overlay."""
    im = nanite_metal(source(name, cut=(37, 41)), cyan_seams)
    out = Image.new("RGBA", im.size)
    out.alpha_composite(im.resize((44, 44), Image.LANCZOS), (2, 2))
    return out


def vault(name: str) -> Image.Image:
    out = craft(name)
    layer = Image.new("RGBA", out.size)
    c, r = 29, 26
    hexagon = [(c + r * dx, c + r * dy) for dx, dy in ((0, -1), (0.87, -0.5), (0.87, 0.5), (0, 1), (-0.87, 0.5), (-0.87, -0.5))]
    ImageDraw.Draw(layer).polygon(hexagon, outline=SEAM + (255,), width=2)
    out.alpha_composite(glow(layer, 1.5))
    out.alpha_composite(layer)
    return out


def foundry(name: str) -> Image.Image:
    out = craft(name)
    glyph(out, 18, (38, 38))
    motes(out, (40, 30), (10, -24), 12, 21)
    return out


ICONS = {"lfg_nanite_armor.dds": armour, "lfg_nanite_swarm_hangar.dds": hangar, "lfg_nanite_reshaper.dds": reshaper,
         "lfg_nanite_siege_driver.dds": siege_driver,
         "lfg_nanite_flak_swarm.dds": flak_swarm,
         "lfg_nanite_disassembler.dds": disassembler,
         "lfg_nanite_storm_autocannon.dds": storm_autocannon,
         "lfg_swarmer_vault.dds": lambda: vault("strike_craft_fighter_3"),
         "lfg_swarmer_foundry.dds": lambda: foundry("strike_craft_fighter_3"),
         "lfg_interdictor_vault.dds": lambda: vault("strike_craft_bomber_3"),
         "lfg_interdictor_foundry.dds": lambda: foundry("strike_craft_bomber_3")}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, make in ICONS.items():
        make().save(OUT / name)
        print(f"wrote {OUT / name}")
