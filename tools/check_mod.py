#!/usr/bin/env python3
"""Static verification for the LFG Traditions mod.

  python3 -I tools/check_mod.py                    # full check (uses installed game + Giga when found)
  python3 -I tools/check_mod.py --require-sources  # fail instead of skipping checks that need game files
  python3 -I tools/check_mod.py --update-snapshot  # refresh tools/data/modifiers_4.5.txt.gz from modifiers.log

Checks that only need the repo (always run, also in CI): file layout, parse errors, localisation format/BOM/duplicates,
tradition tree structure and prerequisites, required localisation keys, sprite definitions, modifier names (against
modifiers.log or the bundled snapshot), key prefixes, descriptor and thumbnail.
Checks that need the installed game / Giga: tree templates, texture files, referenced techs/origins/civics/ethics/
variables, and that the generated vanilla overrides are up to date.
"""
from __future__ import annotations

import argparse
import gzip
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_overrides  # noqa: E402
import pdx  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
STEAM = Path.home() / "Library/Application Support/Steam/steamapps"
DEFAULT_GAME = STEAM / "common/Stellaris"
DEFAULT_GIGA = STEAM / "workshop/content/281990/1121692237"
DEFAULT_MODIFIERS_LOG = Path.home() / "Documents/Paradox Interactive/Stellaris/logs/script_documentation/modifiers.log"
SNAPSHOT = REPO / "tools/data/modifiers_4.5.txt.gz"

# Vanilla tree layouts in interface/topbar_traditions_view.gui (4.5). Used when the game isn't installed.
KNOWN_TREE_TEMPLATES = {
    "tree_11_11_21", "tree_11_111", "tree_11_12_21", "tree_11_12", "tree_111_11", "tree_12_11_11",
    "tree_12_11", "tree_12_12", "tree_21_11", "tree_21_12", "tree_21_21",
}
# Required prerequisites per layout: slot index -> slots it must require (1-based).
TEMPLATE_PREREQS = {"tree_21_11": {4: {1, 2}, 5: {3}}}

ALLOWED_FILES = [
    r"descriptor\.mod",
    r"thumbnail\.png",
    r"common/tradition_categories/[^/]+\.txt",
    r"common/traditions/[^/]+\.txt",
    r"common/governments/civics/[^/]+\.txt",
    r"common/ascension_perks/zz_lfg_[^/]+\.txt",
    r"common/situations/zz_lfg_[^/]+\.txt",
    r"common/script_values/[^/]+\.txt",
    r"interface/[^/]+\.gfx",
    r"localisation/english/[^/]+_l_english\.yml",
]
OVERRIDE_FILES = {Path(p).relative_to("mod").as_posix() for p in gen_overrides.OVERRIDES}
KEY_PREFIXES = ("tradition_lfg_", "tr_lfg_", "civic_lfg_", "lfg_")
LOC_LINE = re.compile(r'^ ([A-Za-z0-9_.\-]+):(\d+)? "(.*)"\s*$')
# Keys whose value is a localisation key.
LOC_VALUE_KEYS = {"desc", "description", "negative_description", "text", "fail_text", "custom_tooltip"}
NOT_MODIFIERS = {"potential", "mult", "desc", "custom_tooltip"}


class Report:
    def __init__(self, require_sources: bool):
        self.failures: List[str] = []
        self.skipped: List[str] = []
        self.require_sources = require_sources

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def skip(self, what: str) -> None:
        if self.require_sources:
            self.fail(f"{what}: game/Giga files not found (--require-sources)")
        else:
            self.skipped.append(what)


class Mod:
    """Parsed view of the mod directory."""

    def __init__(self, root: Path, report: Report):
        self.root = root
        self.report = report
        self.files: Dict[str, List[pdx.Entry]] = {}
        for path in sorted(root.rglob("*")):
            rel = path.relative_to(root).as_posix()
            if path.is_file() and path.suffix in (".txt", ".gfx"):
                try:
                    self.files[rel] = pdx.parse_file(path)
                except (pdx.ParseError, UnicodeDecodeError) as e:
                    report.fail(f"{rel}: parse error: {e}")

    def top(self, folder: str) -> Dict[str, pdx.Entry]:
        out: Dict[str, pdx.Entry] = {}
        for rel, entries in self.files.items():
            if rel.startswith(folder + "/") and rel not in OVERRIDE_FILES:
                for e in entries:
                    if e.key is not None:
                        if e.key in out:
                            self.report.fail(f"{rel}: duplicate definition of {e.key}")
                        out[e.key] = e
        return out


# ------------------------------------------------------------------------------------------------
def check_layout(mod: Mod, r: Report) -> None:
    for path in sorted(mod.root.rglob("*")):
        if path.is_file() and path.name != ".DS_Store":  # Finder junk; install/publish strip it
            rel = path.relative_to(mod.root).as_posix()
            if not any(re.fullmatch(p, rel) for p in ALLOWED_FILES):
                r.fail(f"unexpected file in mod/: {rel}")


def check_descriptor(mod: Mod, r: Report) -> None:
    d = mod.root / "descriptor.mod"
    if not d.exists():
        r.fail("missing descriptor.mod")
        return
    text = d.read_text(encoding="utf-8")
    for field in ("name", "version", "supported_version", "picture"):
        if not re.search(rf'^{field}="[^"]+"', text, re.M):
            r.fail(f"descriptor.mod: missing {field}")
    if re.search(r"^path=", text, re.M):
        r.fail("descriptor.mod: must not contain path=")
    thumb = mod.root / "thumbnail.png"
    if not thumb.exists():
        r.fail("missing thumbnail.png")
    else:
        data = thumb.read_bytes()
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            r.fail("thumbnail.png is not a PNG")
        if len(data) >= 1024 * 1024:
            r.fail(f"thumbnail.png is {len(data)} bytes (Steam limit 1 MB)")


def load_loc(mod: Mod, r: Report) -> Dict[str, str]:
    keys: Dict[str, str] = {}
    for path in sorted((mod.root / "localisation").rglob("*.yml")):
        rel = path.relative_to(mod.root).as_posix()
        raw = path.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            r.fail(f"{rel}: missing UTF-8 BOM")
        lines = raw.decode("utf-8-sig").splitlines()
        if not lines or lines[0].strip() != "l_english:":
            r.fail(f"{rel}: first line must be 'l_english:'")
        for n, line in enumerate(lines[1:], start=2):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = LOC_LINE.match(line)
            if not m:
                r.fail(f"{rel}:{n}: malformed localisation line: {line.strip()[:60]}")
                continue
            key, value = m.group(1), m.group(3)
            if key in keys:
                r.fail(f"{rel}:{n}: duplicate localisation key {key}")
            if value.count("§") and value.count("§!") * 2 != value.count("§"):
                r.fail(f"{rel}:{n}: unbalanced § colour codes in {key}")
            keys[key] = value
    return keys


def check_traditions(mod: Mod, loc: Dict[str, str], templates: Set[str], r: Report) -> None:
    cats = mod.top("common/tradition_categories")
    trads = mod.top("common/traditions")
    owner: Dict[str, str] = {}
    if not cats:
        r.fail("no tradition categories defined")
    for ck, cat in cats.items():
        if not cat.is_block:
            r.fail(f"{ck}: not a block")
            continue
        body = cat.value
        tmpl = pdx.first(body, "tree_template")
        if tmpl is None or tmpl.value not in templates:
            r.fail(f"{ck}: unknown tree_template {getattr(tmpl, 'value', None)!r}")
        tlist = pdx.first(body, "traditions")
        listed = pdx.bare_values(tlist.value) if tlist is not None and tlist.is_block else []
        if len(listed) != 5:
            r.fail(f"{ck}: expected 5 traditions, found {len(listed)}")
        members = list(listed)
        for bonus in ("adoption_bonus", "finish_bonus"):
            e = pdx.first(body, bonus)
            if e is None:
                r.fail(f"{ck}: missing {bonus}")
            else:
                members.append(e.value)
        for t in members:
            if t not in trads:
                r.fail(f"{ck}: tradition {t} is not defined")
            if t in owner:
                r.fail(f"{t}: listed in both {owner[t]} and {ck}")
            owner[t] = ck
        # loc + sprites for the category
        for key in (ck, f"{ck}_desc"):
            if key not in loc:
                r.fail(f"missing localisation: {key}")
        for d in pdx.get(body, "desc"):
            text = d.value if not d.is_block else (pdx.first(d.value, "text") or pdx.Entry(None, None, "", 0)).value
            if text and text not in loc:
                r.fail(f"{ck}: desc key {text} has no localisation")
        for key in members:
            if key not in loc:
                r.fail(f"missing localisation: {key}")
        for key in listed:
            for suffix in ("_desc", "_delayed"):
                if key + suffix not in loc:
                    r.fail(f"missing localisation: {key}{suffix}")
        # prerequisites stay inside the tree and match the layout
        slots = {t: i + 1 for i, t in enumerate(listed)}
        for t in listed:
            if t not in trads or not trads[t].is_block:
                continue
            possible = pdx.first(trads[t].value, "possible")
            reqs = [e.value for e in pdx.walk(possible.value) if e.key == "has_tradition"] \
                if possible is not None and possible.is_block else []
            for req in reqs:
                if req not in slots:
                    r.fail(f"{t}: requires {req}, which is not in {ck}")
            expected = TEMPLATE_PREREQS.get(getattr(tmpl, "value", ""), {}).get(slots[t], set())
            got = {slots[q] for q in reqs if q in slots}
            if tmpl is not None and tmpl.value in TEMPLATE_PREREQS and got != expected:
                r.fail(f"{t}: slot {slots[t]} of {tmpl.value} should require slots {sorted(expected)}, requires {sorted(got)}")
    for t in trads:
        if t not in owner:
            r.fail(f"{t}: defined but not part of any tradition category")


def check_civics(mod: Mod, loc: Dict[str, str], r: Report) -> None:
    for ck, civ in mod.top("common/governments/civics").items():
        for key in (ck, f"{ck}_desc"):
            if key not in loc:
                r.fail(f"missing localisation: {key}")
        if civ.is_block and pdx.first(civ.value, "modifier") is None:
            r.fail(f"{ck}: has no modifier block")


def check_loc_references(mod: Mod, loc: Dict[str, str], r: Report) -> None:
    for rel, entries in mod.files.items():
        for e in pdx.walk(entries):
            if e.key in LOC_VALUE_KEYS and not e.is_block and "lfg" in e.value and e.value not in loc:
                r.fail(f"{rel}:{e.line}: {e.key} = {e.value} has no localisation")


def mod_sprites(mod: Mod, r: Report) -> Dict[str, str]:
    sprites: Dict[str, str] = {}
    for rel, entries in mod.files.items():
        if not rel.endswith(".gfx"):
            continue
        for block in pdx.get(entries, "spriteTypes"):
            for s in block.value if block.is_block else []:
                if not s.is_block:
                    continue
                name, tex = pdx.first(s.value, "name"), pdx.first(s.value, "textureFile")
                if name is None or tex is None:
                    r.fail(f"{rel}:{s.line}: sprite missing name or textureFile")
                    continue
                if name.value in sprites:
                    r.fail(f"{rel}:{s.line}: duplicate sprite {name.value}")
                sprites[name.value] = tex.value
    return sprites


def check_sprites(mod: Mod, game: Optional[Path], r: Report) -> None:
    sprites = mod_sprites(mod, r)
    for ck, cat in mod.top("common/tradition_categories").items():
        for kind in ("hex_bg", "category_bg", "category_tile", "category_icon"):
            if f"GFX_tradition_{kind}_{ck}" not in sprites:
                r.fail(f"{ck}: missing sprite GFX_tradition_{kind}_{ck}")
        tlist = pdx.first(cat.value, "traditions") if cat.is_block else None
        for t in pdx.bare_values(tlist.value) if tlist is not None and tlist.is_block else []:
            if f"GFX_{t}" not in sprites:
                r.fail(f"{t}: missing sprite GFX_{t}")
    textures = set(sprites.values())
    for civ in mod.top("common/governments/civics").values():
        icon = pdx.first(civ.value, "icon") if civ.is_block else None
        if icon is not None:
            textures.add(icon.value)
    if game is None:
        r.skip("texture files exist")
        return
    for tex in sorted(textures):
        if not ((mod.root / tex).exists() or (game / tex).exists()):
            r.fail(f"texture not found in mod or game: {tex}")


def load_modifiers(log: Optional[Path]) -> Set[str]:
    if log is not None and log.exists():
        text = log.read_text(encoding="utf-8", errors="replace")
        return set(re.findall(r"^- ([A-Za-z0-9_@]+), Category", text, re.M))
    with gzip.open(SNAPSHOT, "rt", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def modifier_keys(mod: Mod):
    for folder in ("common/traditions", "common/governments/civics"):
        for key, e in mod.top(folder).items():
            if not e.is_block:
                continue
            for block in pdx.get(e.value, "modifier") + pdx.get(e.value, "triggered_modifier"):
                for m in block.value if block.is_block else []:
                    if m.key and m.key not in NOT_MODIFIERS:
                        yield key, m


def check_modifiers(mod: Mod, known: Set[str], r: Report) -> None:
    for owner, m in modifier_keys(mod):
        if m.key not in known:
            r.fail(f"{owner}: unknown modifier {m.key}")
        if m.is_block or not re.fullmatch(r"-?\d+(\.\d+)?|@[A-Za-z0-9_]+", m.value):
            r.fail(f"{owner}: modifier {m.key} has non-numeric value {m.value!r}")


def check_prefixes(mod: Mod, loc: Dict[str, str], r: Report) -> None:
    for rel, entries in mod.files.items():
        if not rel.startswith("common/") or rel in OVERRIDE_FILES:
            continue
        for e in entries:
            if e.key is not None and not e.key.startswith(KEY_PREFIXES):
                r.fail(f"{rel}:{e.line}: top-level key {e.key} lacks an lfg prefix")
    for key in loc:
        if "lfg" not in key:
            r.fail(f"localisation key {key} lacks an lfg prefix (could overwrite vanilla/other mods)")


# --- needs game / Giga --------------------------------------------------------------------------
def defined_keys(dirs: List[Path], folder: str) -> Set[str]:
    out: Set[str] = set()
    for d in dirs:
        for path in (d / folder).rglob("*.txt") if (d / folder).exists() else []:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            out.update(re.findall(r"^([A-Za-z0-9_\.]+)\s*=\s*\{", text, re.M))
    return out


def defined_variables(dirs: List[Path]) -> Set[str]:
    out: Set[str] = set()
    for d in dirs:
        for path in (d / "common/scripted_variables").rglob("*.txt") if (d / "common/scripted_variables").exists() else []:
            out.update(re.findall(r"^(@[A-Za-z0-9_]+)\s*=", path.read_text(encoding="utf-8-sig", errors="replace"), re.M))
    return out


def check_references(mod: Mod, game: Optional[Path], giga: Optional[Path], r: Report) -> None:
    if game is None or giga is None:
        r.skip("referenced techs/origins/civics/ethics/variables exist")
        return
    dirs = [game, giga, mod.root]
    techs = defined_keys(dirs, "common/technology")
    civics = defined_keys(dirs, "common/governments/civics")  # civics and origins
    ethics = defined_keys(dirs, "common/ethics")
    trads = defined_keys(dirs, "common/traditions")
    variables = defined_variables([game, giga])
    lookups = {"has_technology": techs, "has_origin": civics, "has_valid_civic": civics, "has_civic": civics,
               "has_ethic": ethics, "has_tradition": trads}
    for rel, entries in mod.files.items():
        if not rel.startswith("common/") or rel in OVERRIDE_FILES:
            continue
        for e in pdx.walk(entries):
            if not e.is_block and e.key in lookups and e.value not in lookups[e.key]:
                r.fail(f"{rel}:{e.line}: {e.key} = {e.value} is not defined in the game, Giga or this mod")
            if not e.is_block and isinstance(e.value, str) and e.value.startswith("@") and e.value not in variables:
                r.fail(f"{rel}:{e.line}: scripted variable {e.value} is not defined")
            if e.key in ("origin", "civics", "ethics") and e.is_block:
                pool = ethics if e.key == "ethics" else civics
                for v in pdx.walk(e.value):
                    if v.key == "value" and v.value not in pool:
                        r.fail(f"{rel}:{v.line}: {e.key} value {v.value} is not defined")


def check_overrides(mod: Mod, game: Optional[Path], r: Report) -> None:
    script_values = mod.top("common/script_values")
    for rel in OVERRIDE_FILES:
        for e in pdx.walk(mod.files.get(rel, [])):
            if not e.is_block and isinstance(e.value, str) and e.value.startswith("value:lfg_"):
                if e.value[len("value:"):] not in script_values:
                    r.fail(f"{rel}:{e.line}: {e.value} is not defined in common/script_values")
    if game is None:
        r.skip("vanilla overrides are up to date")
        return
    try:
        generated = gen_overrides.generate(game)
    except (gen_overrides.GenError, OSError) as e:
        r.fail(f"tools/gen_overrides.py fails against the installed game: {e}")
        return
    for out_rel, content in generated.items():
        path = mod.root.parent / out_rel
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            r.fail(f"{out_rel} is stale: run python3 -I tools/gen_overrides.py and review the diff")


def tree_templates(game: Optional[Path], r: Report) -> Set[str]:
    gui = game / "interface/topbar_traditions_view.gui" if game else None
    if gui is None or not gui.exists():
        r.skip("tree templates from the installed game (using the built-in 4.5 list)")
        return KNOWN_TREE_TEMPLATES
    return set(re.findall(r'name = "(tree_[0-9_]+)"', gui.read_text(encoding="utf-8-sig", errors="replace")))


def run(mod_dir: Path, game: Optional[Path], giga: Optional[Path], modifiers_log: Optional[Path],
        require_sources: bool = False) -> Report:
    r = Report(require_sources)
    game = game if game is not None and game.exists() else None
    giga = giga if giga is not None and giga.exists() else None
    mod = Mod(mod_dir, r)
    check_layout(mod, r)
    check_descriptor(mod, r)
    loc = load_loc(mod, r)
    check_traditions(mod, loc, tree_templates(game, r), r)
    check_civics(mod, loc, r)
    check_loc_references(mod, loc, r)
    check_sprites(mod, game, r)
    check_modifiers(mod, load_modifiers(modifiers_log), r)
    check_prefixes(mod, loc, r)
    check_references(mod, game, giga, r)
    check_overrides(mod, game, r)
    return r


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify the LFG Traditions mod.")
    ap.add_argument("--mod", type=Path, default=REPO / "mod")
    ap.add_argument("--game", type=Path, default=Path(os.environ.get("STELLARIS_GAME", DEFAULT_GAME)))
    ap.add_argument("--giga", type=Path, default=Path(os.environ.get("GIGA_DIR", DEFAULT_GIGA)))
    ap.add_argument("--modifiers-log", type=Path, default=DEFAULT_MODIFIERS_LOG)
    ap.add_argument("--snapshot-only", action="store_true", help="ignore modifiers.log, use the bundled snapshot")
    ap.add_argument("--require-sources", action="store_true")
    ap.add_argument("--update-snapshot", action="store_true")
    args = ap.parse_args(argv)

    if args.update_snapshot:
        names = load_modifiers(args.modifiers_log) if args.modifiers_log.exists() else set()
        if not names:
            print(f"check_mod: {args.modifiers_log} not found", file=sys.stderr)
            return 1
        body = "# Modifier names from Stellaris script_documentation/modifiers.log (with Gigastructural loaded).\n" \
               "# Regenerate: python3 -I tools/check_mod.py --update-snapshot\n" + "\n".join(sorted(names)) + "\n"
        with gzip.GzipFile(SNAPSHOT, "wb", compresslevel=9, mtime=0) as f:
            f.write(body.encode("utf-8"))
        print(f"wrote {SNAPSHOT.relative_to(REPO)} ({len(names)} modifiers)")
        return 0

    log = None if args.snapshot_only else args.modifiers_log
    r = run(args.mod, args.game, args.giga, log, args.require_sources)
    for s in r.skipped:
        print(f"  skip  {s}")
    for f in r.failures:
        print(f"  FAIL  {f}")
    if r.failures:
        print(f"check_mod: {len(r.failures)} problem(s)")
        return 1
    print("check_mod: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
