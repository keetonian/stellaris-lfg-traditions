"""Builds the 64x64 district specialization icon for Penal Matter Compactors from Gigastructural's 32x32 resource icons.

Needs Pillow (reads and writes .dds); not part of the stdlib-only tooling. Run from the repo root:
  python3 art/make_zone_icons.py
"""
from pathlib import Path
from PIL import Image

GIGA = Path.home() / "Library/Application Support/Steam/steamapps/workshop/content/281990/1121692237"
OUT = Path("mod/gfx/interface/icons/districts")
# Penal Supertensile Works uses Gigastructural's own 64x64 GFX_giga_district_specialization_supertensiles instead.
ICONS = {
    "lfg_zone_penal_bulk_matter.dds": "giga_sr_bulk_matter_large.dds",
}

OUT.mkdir(parents=True, exist_ok=True)
for out, src in ICONS.items():
    im = Image.open(GIGA / "gfx/interface/icons/resources" / src).convert("RGBA")
    im.resize((64, 64), Image.LANCZOS).save(OUT / out)  # vanilla specialization icons are 64x64
    print("wrote", OUT / out)
