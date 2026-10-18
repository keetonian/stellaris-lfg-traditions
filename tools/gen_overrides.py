#!/usr/bin/env python3
"""Generates the mod's overrides of vanilla definitions from the installed game files.

Each override is a verbatim copy of one vanilla top-level block with a snippet inserted after an anchor,
so the diff against vanilla is exactly the intended change. Run after every game update.

  python3 -I tools/gen_overrides.py          # (re)write the override files
  python3 -I tools/gen_overrides.py --check  # exit 1 if the files differ from a fresh generation
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_GAME = Path.home() / "Library/Application Support/Steam/steamapps/common/Stellaris"

FLESH_BLOCK = """\t\tcustom_tooltip = {
\t\t\tfail_text = "lfg_requires_not_pampered_masters"
\t\t\tNOT = { has_valid_civic = civic_lfg_pampered_masters }
\t\t}
"""

SYNTH_FERTILITY_BLOCK = """\t\tmodifier = {
\t\t\tadd = value:lfg_synthetic_fertility_acceleration
\t\t\tdesc = lfg_situation_synthetic_fertility_acceleration_desc
\t\t}
"""

RESORT_DISTRICT_BLOCK = """\ttriggered_planet_modifier = {
\t\tpotential = {
\t\t\texists = owner
\t\t\towner = {
\t\t\t\tis_regular_empire = yes
\t\t\t\thas_active_tradition = tr_lfg_resorts_hospitality_academies
\t\t\t}
\t\t}
\t\tmodifier = {
\t\t\tjob_resort_worker_add = @lfg_resort_extra_district_jobs
\t\t}
\t}
\ttriggered_planet_modifier = {
\t\tpotential = {
\t\t\texists = owner
\t\t\towner = {
\t\t\t\tis_regular_empire = yes
\t\t\t\thas_active_tradition = tr_lfg_resorts_wonders_of_the_galaxy
\t\t\t}
\t\t}
\t\tmodifier = {
\t\t\tplanet_max_districts_add = @lfg_resort_districts_per_district
\t\t}
\t}
"""

def holomuseum_block(research: str) -> str:
    """Galactic Broadcast - Holo-Museums: the museum's regular-empire entertainer bonuses again (not its upkeep),
    like vanilla's Archaeoengineers block in the same building."""
    return f"""\ttriggered_planet_modifier = {{
\t\tpotential = {{
\t\t\texists = owner
\t\t\towner = {{
\t\t\t\tis_regular_empire = yes
\t\t\t\thas_active_tradition = tr_lfg_broadcast_holo_museums
\t\t\t}}
\t\t}}
\t\tplanet_entertainers_unity_produces_add = 0.25
\t\tplanet_entertainers_{research}_research_produces_add = 0.25
\t}}
"""


def holomuseum_anchor(research: str) -> str:
    """The building's regular-empire block granting entertainer unity, research and consumer goods upkeep."""
    return (r"^\ttriggered_planet_modifier = \{\n\t\tpotential = \{\n\t\t\texists = owner\n\t\t\towner = \{\n"
            r"\t\t\t\tis_regular_empire = yes\n\t\t\t\}\n\t\t\}\n"
            r"\t\tplanet_entertainers_unity_produces_add = 0\.25\n"
            rf"\t\tplanet_entertainers_{research}_research_produces_add = 0\.25\n"
            r"\t\tplanet_entertainers_consumer_goods_upkeep_add = 0\.25\n\t\}\n")


HOLOMUSEUMS = "common/buildings/21_grand_archive_buildings.txt"

# out file -> list of (vanilla source file, top-level key, anchor regex, snippet inserted after the anchor)
OVERRIDES = {
    "mod/common/ascension_perks/zz_lfg_ascension_path_overrides.txt": [
        ("common/ascension_perks/00_ascension_paths.txt", "ap_the_flesh_is_weak", r"^\tpossible = \{\n", FLESH_BLOCK),
        ("common/ascension_perks/00_ascension_paths.txt", "ap_synthetic_evolution", r"^\tpossible = \{\n", FLESH_BLOCK),
    ],
    "mod/common/districts/zz_lfg_district_overrides.txt": [
        # Accommodation District: the regular-empire block that grants its resort workers, then our extra block.
        ("common/districts/00_urban_districts.txt", "district_resort",
         r"^\ttriggered_planet_modifier = \{\n\t\tpotential = \{\n\t\t\texists = owner\n\t\t\towner = \{\n"
         r"\t\t\t\tis_regular_empire = yes\n\t\t\t\}\n\t\t\}\n\t\tmodifier = \{\n"
         r"\t\t\tjob_resort_worker_add = @special_district_jobs\n\t\t\}\n\t\}\n", RESORT_DISTRICT_BLOCK),
    ],
    "mod/common/buildings/zz_lfg_building_overrides.txt": [
        (HOLOMUSEUMS, "xeno_geology_holomuseum", holomuseum_anchor("engineering"), holomuseum_block("engineering")),
        (HOLOMUSEUMS, "aesthetic_wonders_holomuseum", holomuseum_anchor("physics"), holomuseum_block("physics")),
        (HOLOMUSEUMS, "galactic_history_holomuseum", holomuseum_anchor("society"), holomuseum_block("society")),
    ],
    "mod/common/situations/zz_lfg_situation_overrides.txt": [
        ("common/situations/08_machine_age_situations.txt", "situation_synthetic_fertility_digitization",
         r"^\tmonthly_progress = \{\n\t\tbase = 15\n", SYNTH_FERTILITY_BLOCK),
    ],
}


class GenError(RuntimeError):
    pass


def extract_block(text: str, key: str) -> str:
    """Returns the full text of the top-level `key = { ... }` block (through its closing brace and newline)."""
    matches = list(re.finditer(rf"^{re.escape(key)}\s*=\s*\{{", text, re.M))
    if len(matches) != 1:
        raise GenError(f"expected exactly one top-level '{key} = {{', found {len(matches)}")
    start = matches[0].start()
    depth = 0
    i = matches[0].end() - 1
    in_string = in_comment = False
    while i < len(text):
        c = text[i]
        if in_comment:
            in_comment = c != "\n"
        elif in_string:
            in_string = c != '"'
        elif c == "#":
            in_comment = True
        elif c == '"':
            in_string = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = text.find("\n", i)
                return text[start:(len(text) if end == -1 else end + 1)]
        i += 1
    raise GenError(f"unclosed block for '{key}'")


def game_version(game: Path) -> str:
    try:
        m = re.search(r'"rawVersion"\s*:\s*"([^"]+)"', (game / "launcher-settings.json").read_text())
        return m.group(1) if m else "unknown"
    except OSError:
        return "unknown"


def generate(game: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for out_path, items in OVERRIDES.items():
        parts = [
            "# GENERATED by tools/gen_overrides.py - do not edit by hand.\n",
            f"# Verbatim copies of vanilla definitions (Stellaris {game_version(game)}) with marked LFG additions.\n",
            "# The zz_ file name makes these load after (and replace) the vanilla definitions.\n",
        ]
        for src, key, anchor, snippet in items:
            text = (game / src).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
            block = extract_block(text, key)
            hits = list(re.finditer(anchor, block, re.M))
            if len(hits) != 1:
                raise GenError(f"{key}: anchor {anchor!r} matched {len(hits)} times in {src} (expected 1)")
            cut = hits[0].end()
            indent = re.match(r"\t*", snippet).group(0)
            marked = f"{indent}# LFG: added by stellaris-lfg-traditions\n" + snippet
            parts.append(f"\n# from {src}\n" + block[:cut] + marked + block[cut:])
        out[out_path] = "".join(parts)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="only compare, don't write")
    ap.add_argument("--game", type=Path, default=Path(os.environ.get("STELLARIS_GAME", DEFAULT_GAME)))
    ap.add_argument("--repo", type=Path, default=REPO)
    args = ap.parse_args(argv)
    try:
        generated = generate(args.game)
    except (GenError, OSError) as e:
        print(f"gen_overrides: error: {e}", file=sys.stderr)
        return 1
    stale = []
    for rel, content in generated.items():
        path = args.repo / rel
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if args.check:
            if current != content:
                stale.append(rel)
        elif current != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {rel}")
    if stale:
        print("gen_overrides: stale (run tools/gen_overrides.py): " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
