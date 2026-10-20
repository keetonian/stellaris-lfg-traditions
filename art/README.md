# Workshop thumbnail

`mod/thumbnail.png` (sent to Steam as the preview on every `scripts/publish.sh` upload) is a 640×640 crop of a
Stellaris loading screen with the title on top. Candidates are in `thumbnail_candidates/`:

| File | Source (game `gfx/loadingscreens/`) | Fits |
|---|---|---|
| `dyson_sphere.png` (current) | `load_10.dds` | megastructures, Gigastructural |
| `ring_landscape.png` | `load_20.dds` | artificial worlds, resorts, farms |
| `habitat_city.png` | `load_15.dds` | habitats, city life |

To make another (needs Pillow, which can read `.dds`; not part of the stdlib-only tooling):

```sh
G="$HOME/Library/Application Support/Steam/steamapps/common/Stellaris/gfx/loadingscreens"
python3 art/dds2png.py "$G" /tmp/thumbs load_10            # writes /tmp/thumbs/load_10.png (+ sheet.png)
python3 art/make_thumbnail.py /tmp/thumbs/load_10.png 0.40 mod/thumbnail.png   # 0.40 = horizontal crop centre (0-1)
```

Keep it under 1 MB (Steam's limit; `tools/check_mod.py` checks it).

# District specialization icons

Penal Supertensile Works uses Gigastructural's own 64x64 specialization icon (`GFX_giga_district_specialization_supertensiles`).
Gigastructural has none for bulk matter, so `mod/gfx/interface/icons/districts/lfg_zone_penal_bulk_matter.dds` is its
32x32 bulk matter resource icon upscaled to vanilla's 64x64: `python3 art/make_zone_icons.py` (Pillow).

# Civic icons

Every civic from this mod has the same colour: `python3 art/make_civic_icons.py` (Pillow) takes a vanilla civic icon
(listed in `ICONS`) and recolours it to `CIVIC_COLOR` (amber; vanilla's are teal), keeping its shading.
Output: `mod/gfx/interface/icons/governments/civics/civic_lfg_<name>.dds`, referenced by the civic's `icon`.
A new civic needs an entry in `ICONS`.

# Origin art

The Nanite Forge origin's icon and picture: `python3 art/make_origin_art.py` (Pillow). The icon is a diamond in vanilla's
origin-icon colours with vanilla's nanite symbol as the glyph (`mod/gfx/interface/icons/origins/lfg_origin_nanite_forge.dds`);
the Nanite Substrate trait icon is a teal disc like vanilla's positive trait icons with the same symbol
(`mod/gfx/interface/icons/traits/trait_lfg_nanite_substrate.dds`); the picture is a 220x115 crop of vanilla's "gray gooed planet" event picture
(`mod/gfx/event_pictures/origins/lfg_origin_nanite_forge.dds`, sprite `GFX_origin_lfg_nanite_forge` in
`mod/interface/lfg_megastructures.gfx`).
