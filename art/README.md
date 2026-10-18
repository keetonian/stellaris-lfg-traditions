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
