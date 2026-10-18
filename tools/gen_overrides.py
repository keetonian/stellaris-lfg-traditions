#!/usr/bin/env python3
"""Generates the mod's overrides of vanilla/Gigastructural definitions from the installed game and Giga files.

Each override is a verbatim copy of one top-level block (or, for an inline script, the whole file) with a snippet
inserted after an anchor, so the diff against the source is exactly the intended change. Run after every game or
Giga update. Also writes the Shelve edicts and their localisation from the SHELVE table, so the edicts and the
tech overrides that check them can't drift apart.

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
STEAM = Path.home() / "Library/Application Support/Steam/steamapps"
DEFAULT_GAME = STEAM / "common/Stellaris"
DEFAULT_GIGA = STEAM / "workshop/content/281990/1121692237"
# Sources starting with this prefix are read from the Gigastructural directory instead of the game.
GIGA = "giga:"

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

# Curated Progress (ap_lfg_curated_progress): one perpetual Shelve edict per repeatable tech. While an edict is
# active, the tech's weight_modifier gets factor 0, so it is no longer drawn as a research option.
# (edict suffix, tech key, research area, source file, extra potential trigger: when the tech can show up at all)
_ENG = "common/technology/00_eng_tech_repeatable.txt"
_PHYS = "common/technology/00_phys_tech_repeatable.txt"
_SOC = "common/technology/00_soc_tech_repeatable.txt"
SHELVE = [
    ("mineral_output", "tech_repeatable_improved_tile_mineral_output", "engineering", _ENG,
     "has_technology = tech_mineral_purification_2"),
    ("station_damage", "tech_repeatable_improved_military_station_damage", "engineering", _ENG,
     "has_technology = tech_defense_platform_hull_1"),
    ("station_health", "tech_repeatable_improved_military_station_health", "engineering", _ENG,
     "has_technology = tech_defense_platform_hull_1"),
    ("armor", "tech_repeatable_improved_armor_output", "engineering", _ENG, "has_technology = tech_ship_armor_3"),
    ("explosive_damage", "tech_repeatable_weapon_type_explosive_damage", "engineering", _ENG,
     "OR = { has_technology = tech_missiles_3 has_technology = tech_swarmer_missiles_2 }"),
    ("explosive_fire_rate", "tech_repeatable_weapon_type_explosive_fire_rate", "engineering", _ENG,
     "OR = { has_technology = tech_missiles_3 has_technology = tech_swarmer_missiles_2 }"),
    ("kinetic_damage", "tech_repeatable_weapon_type_kinetic_damage", "engineering", _ENG,
     "has_technology = tech_mass_drivers_3"),
    ("kinetic_fire_rate", "tech_repeatable_weapon_type_kinetic_fire_rate", "engineering", _ENG,
     "has_technology = tech_mass_drivers_3"),
    ("blokkat_scrap_damage", "giga_tech_blokkat_scrap_damage", "engineering", GIGA + "common/technology/giga_13_blokkat.txt",
     "has_country_flag = researching_blokkat_scrap_damage"),
    ("energy_output", "tech_repeatable_improved_tile_energy_output", "physics", _PHYS,
     "has_technology = tech_power_plant_3"),
    ("shields", "tech_repeatable_improved_shield_output", "physics", _PHYS, "has_technology = tech_shields_4"),
    ("energy_damage", "tech_repeatable_weapon_type_energy_damage", "physics", _PHYS, "has_technology = tech_lasers_4"),
    ("energy_fire_rate", "tech_repeatable_weapon_type_energy_fire_rate", "physics", _PHYS,
     "has_technology = tech_lasers_2"),
    ("dimensional_storage", "giga_tech_repeatable_dimensional_storage", "physics",
     GIGA + "common/technology/giga_04_repeatables.txt", "has_technology = giga_tech_tetradimensional_engineering"),
    ("food_output", "tech_repeatable_improved_tile_food_output", "society", _SOC, "has_technology = tech_gene_crops"),
    ("core_system_cap", "tech_repeatable_improved_core_system_cap", "society", _SOC,
     "has_technology = tech_galactic_bureaucracy"),
    ("army_damage", "tech_repeatable_improved_army_damage", "society", _SOC, "has_technology = tech_combat_training"),
    ("army_health", "tech_repeatable_improved_army_health", "society", _SOC, "has_technology = tech_combat_training"),
    ("leader_life_span", "tech_repeatable_improved_leader_life_span", "society", _SOC,
     "has_technology = tech_vitality_boosters"),
    ("strike_craft_damage", "tech_repeatable_weapon_type_strike_craft_fire_damage", "society", _SOC,
     "has_technology = tech_strike_craft_3"),
    ("strike_craft_fire_rate", "tech_repeatable_weapon_type_strike_craft_fire_rate", "society", _SOC,
     "has_technology = tech_strike_craft_3"),
    ("blokkat_scrap_research", "giga_tech_blokkat_scrap_research", "society", GIGA + "common/technology/giga_13_blokkat.txt",
     "has_country_flag = researching_blokkat_scrap_research"),
    ("frameworld_outposts", "tech_frameworld_repeatable_outpost_output", "society",
     GIGA + "common/technology/giga_16_frameworld.txt", "giga_has_frameworld_origin = yes"),
    ("eawaf_weapons", "giga_tech_eawaf_weapons_repeatable", "society", GIGA + "common/technology/giga_18_eawaf.txt",
     "has_country_flag = giga_tech_eawaf_weapons_repeatable_possible"),
]
# Gigastructural's ~50 megastructure capacity repeatables share one inline script; it gets one check per area.
MEGA_CAP_AREAS = ("engineering", "physics", "society")
MEGA_CAP_SCRIPT = "common/inline_scripts/technology/giga_mega_repeatable.txt"
MEGA_CAP_EDICT = "lfg_shelve_megastructure_capacity_$area$"
AREA_NAMES = {"engineering": "Engineering", "physics": "Physics", "society": "Society"}


def shelve_edict(suffix: str) -> str:
    return f"lfg_shelve_{suffix}"


def shelve_tech_block(edict: str, indent: str = "\t\t") -> str:
    inner = indent + ("\t" if indent.startswith("\t") else "    ")
    return f"{indent}modifier = {{\n{inner}factor = 0\n{inner}has_edict = {edict}\n{indent}}}\n"

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
    # Shelve edicts: vanilla and Gigastructural repeatables. zz_lfg_ sorts after Giga's zz_giga_ tech files.
    "mod/common/technology/zz_lfg_repeatable_overrides.txt": [
        (src, tech, r"^\tweight_modifier = \{\n", shelve_tech_block(shelve_edict(suffix)))
        for suffix, tech, _area, src, _potential in SHELVE
    ],
    # Inline scripts can only be replaced as a whole file (same path; this mod loads after Giga). key None = whole file.
    "mod/" + MEGA_CAP_SCRIPT: [
        (GIGA + MEGA_CAP_SCRIPT, None, r"^    weight_modifier = \{\n", shelve_tech_block(MEGA_CAP_EDICT, "        ")),
    ],
}
SHELVE_EDICTS_FILE = "mod/common/edicts/lfg_shelve_edicts.txt"
SHELVE_LOC_FILE = "mod/localisation/english/lfg_shelve_l_english.yml"


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


def giga_version(giga: Path) -> str:
    try:
        m = re.search(r'^version\s*=\s*"([^"]+)"', (giga / "descriptor.mod").read_text(encoding="utf-8-sig"), re.M)
        return m.group(1) if m else "unknown"
    except OSError:
        return "unknown"


def read_source(src: str, game: Path, giga: Path) -> str:
    path = giga / src[len(GIGA):] if src.startswith(GIGA) else game / src
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def generate_shelve_edicts() -> str:
    lines = [
        "# GENERATED by tools/gen_overrides.py from its SHELVE table - do not edit by hand.\n",
        "# Curated Progress (ap_lfg_curated_progress): perpetual edicts that stop a repeatable tech from being drawn\n",
        "# as a research option (the tech overrides check has_edict). Costs scale with empire size like vanilla edicts.\n",
    ]
    entries = [(shelve_edict(suffix), area, potential) for suffix, _tech, area, _src, potential in SHELVE]
    entries += [(MEGA_CAP_EDICT.replace("$area$", area), area, None) for area in MEGA_CAP_AREAS]
    for edict, area, potential in entries:
        relevant = (f"\t\tOR = {{\n\t\t\thas_edict = {edict}\n\t\t\t{potential}\n\t\t}}\n" if potential else "")
        lines.append(f"""
{edict} = {{
\tlength = -1 # perpetual (vanilla @EdictPerpetual)
\ticon = "GFX_edict_type_policy"
\tresources = {{
\t\tcategory = edicts
\t\tcost = {{
\t\t\tunity = @lfg_shelve_unity_cost
\t\t\tinfluence = @lfg_shelve_influence_cost
\t\t\tmultiplier = value:edict_size_effect
\t\t}}
\t\tupkeep = {{
\t\t\t{area}_research = @lfg_shelve_research_upkeep
\t\t\tmultiplier = value:edict_size_effect
\t\t}}
\t}}
\tpotential = {{
\t\thas_ascension_perk = ap_lfg_curated_progress
{relevant}\t}}
\tai_weight = {{
\t\tweight = 0
\t}}
}}
""")
    return "".join(lines)


def generate_shelve_loc() -> str:
    lines = ["\ufeffl_english:\n",
             " # GENERATED by tools/gen_overrides.py from its SHELVE table - do not edit by hand.\n"]
    for suffix, tech, _area, _src, _potential in SHELVE:
        key = "edict_" + shelve_edict(suffix)
        lines.append(f' {key}:0 "Shelve: ${tech}$"\n')
        lines.append(f' {key}_desc:0 "Our researchers stop pursuing §Y${tech}$§!: it is no longer offered as a '
                     f'research option while this edict is active."\n')
    for area in MEGA_CAP_AREAS:
        key = "edict_" + MEGA_CAP_EDICT.replace("$area$", area)
        name = AREA_NAMES[area]
        lines.append(f' {key}:0 "Shelve: {name} Megastructure Capacity"\n')
        lines.append(f' {key}_desc:0 "Our researchers stop pursuing Gigastructural\'s {area} megastructure capacity '
                     f'repeatables (§Y+1 capacity§! for one megastructure type each): they are no longer offered as research options '
                     f'while this edict is active."\n')
    return "".join(lines)


def generate(game: Path, giga: Path = DEFAULT_GIGA) -> dict[str, str]:
    out: dict[str, str] = {}
    for out_path, items in OVERRIDES.items():
        from_giga = any(src.startswith(GIGA) for src, *_ in items)
        sources = f"Stellaris {game_version(game)}" + (f", Gigastructural {giga_version(giga)}" if from_giga else "")
        parts = [
            "# GENERATED by tools/gen_overrides.py - do not edit by hand.\n",
            f"# Verbatim copies of vanilla/Gigastructural definitions ({sources}) with marked LFG additions.\n",
            "# The zz_ file name (or, for inline scripts, the same path in a later-loading mod) makes these replace the originals.\n",
        ]
        for src, key, anchor, snippet in items:
            text = read_source(src, game, giga)
            block = text if key is None else extract_block(text, key)
            name = key or src
            hits = list(re.finditer(anchor, block, re.M))
            if len(hits) != 1:
                raise GenError(f"{name}: anchor {anchor!r} matched {len(hits)} times in {src} (expected 1)")
            cut = hits[0].end()
            indent = re.match(r"[ \t]*", snippet).group(0)
            marked = f"{indent}# LFG: added by stellaris-lfg-traditions\n" + snippet
            body = block[:cut] + marked + block[cut:]
            parts.append(f"\n# from {src.replace(GIGA, 'Gigastructural ')}\n" + body + ("" if body.endswith("\n") else "\n"))
        out[out_path] = "".join(parts)
    out[SHELVE_EDICTS_FILE] = generate_shelve_edicts()
    out[SHELVE_LOC_FILE] = generate_shelve_loc()
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="only compare, don't write")
    ap.add_argument("--game", type=Path, default=Path(os.environ.get("STELLARIS_GAME", DEFAULT_GAME)))
    ap.add_argument("--giga", type=Path, default=Path(os.environ.get("GIGA_DIR", DEFAULT_GIGA)))
    ap.add_argument("--repo", type=Path, default=REPO)
    args = ap.parse_args(argv)
    try:
        generated = generate(args.game, args.giga)
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
