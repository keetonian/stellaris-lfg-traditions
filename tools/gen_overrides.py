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

# Upload the extra pops too: vanilla's machine_age.3325 uploads up to 15 pops/month to match the base 15 progress.
SYNTH_FERTILITY_UPLOAD = """\t\t\tlfg_synthetic_fertility.1 # Upload one extra pop per extra point of progress
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

def resort_zone_block(job: str, amount: str) -> str:
    """Hospitality Academies: +50% of a resort-world zone's jobs (like vanilla's tr_mercantile_commercial_enterprise
    in jobs/zone_resort_worker_add). Resort and Pleasure Worlds are both resort_colony planets."""
    return f"""\ttriggered_district_planet_modifier = {{
\t\tpotential = {{
\t\t\texists = owner
\t\t\towner = {{
\t\t\t\tis_regular_empire = yes
\t\t\t\thas_active_tradition = tr_lfg_resorts_hospitality_academies
\t\t\t}}
\t\t\thas_modifier = resort_colony
\t\t}}
\t\tjob_{job}_add = {amount}
\t\tmult = 0.5
\t}}
"""


# Resort-world district specializations (zones in the resort / resort_attraction sets) and the job each adds.
RESORT_ZONES = [
    ("zone_resort", "resort_worker", "@scaling_district_1_job"),
    ("zone_resort_entertainment", "entertainer", "@scaling_district_1_job"),
    ("zone_resort_zoo", "biologist", "@doubled_scaling_district_1_job"),
    ("zone_resort_grand_museum", "bureaucrat", "@doubled_scaling_district_1_job"),
    ("zone_resort_hunting_ground", "wrangler", "@doubled_scaling_district_1_job"),
    ("zone_resort_spiritual_retreat", "bureaucrat", "@doubled_scaling_district_1_job"),
    ("zone_resort_restoration_enclave", "healthcare", "@doubled_scaling_district_1_job"),
    ("zone_resort_proving_grounds", "entertainer", "@doubled_scaling_district_1_job"),
]
ZONE_SETS_ANCHOR = r"^\tzone_sets = \{\n(?:\t\t\w+\n)+\t\}\n"


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

# Synthetic Age transformation, stage 4 path choice: individual machines with Giga's ring-megastructure origins
# can't pick Virtuality (option c). `allow` greys the option out with the reason.
VIRTUALITY_BLOCK = """\t\tallow = {
\t\t\towner = {
\t\t\t\tcustom_tooltip = {
\t\t\t\t\tfail_text = "lfg_virtuality_blocked_by_origin"
\t\t\t\t\tNAND = {
\t\t\t\t\t\tis_individual_machine = yes
\t\t\t\t\t\tOR = {
\t\t\t\t\t\t\thas_origin = origin_great_ring
\t\t\t\t\t\t\thas_origin = origin_alderson
\t\t\t\t\t\t}
\t\t\t\t\t}
\t\t\t\t}
\t\t\t}
\t\t}
"""
# Keys starting with this are event ids: the override copies the top-level event block with that id.
EVENT = "event:"

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
# What one level of each shelved tech gives, shown in the edict's description so players needn't remember tech names.
# (edict suffix -> (text, evidence)): evidence must appear in the tech's definition, so a game/Giga update that changes
# the value makes generation fail instead of leaving a stale tooltip. None = no modifier in the tech to check.
SHELVE_EFFECTS = {
    "mineral_output": ("§G+5%§! mineral output from jobs", "planet_jobs_minerals_produces_mult = 0.05"),
    "station_damage": ("§G+10%§! defense platform damage", "shipclass_military_station_damage_mult = 0.1"),
    "station_health": ("§G+10%§! defense platform hull", "shipclass_military_station_hull_mult = 0.1"),
    "armor": ("§G+5%§! ship armor", "ship_armor_mult = 0.05"),
    "explosive_damage": ("§G+5%§! explosive weapon damage (missiles, torpedoes)", "weapon_type_explosive_weapon_damage_mult = 0.05"),
    "explosive_fire_rate": ("§G+5%§! explosive weapon fire rate (missiles, torpedoes)", "weapon_type_explosive_weapon_fire_rate_mult = 0.05"),
    "kinetic_damage": ("§G+5%§! kinetic weapon damage", "weapon_type_kinetic_weapon_damage_mult = 0.05"),
    "kinetic_fire_rate": ("§G+5%§! kinetic weapon fire rate", "weapon_type_kinetic_weapon_fire_rate_mult = 0.05"),
    "blokkat_scrap_damage": ("§G+5%§! ship weapon damage and §G+15%§! damage against Blokkat stripminers",
                             "damage_vs_country_type_blokkat_stripminers_mult = 0.15"),
    "energy_output": ("§G+5%§! energy output from jobs", "planet_jobs_energy_produces_mult = 0.05"),
    "shields": ("§G+5%§! ship shields", "ship_shield_mult = 0.05"),
    "energy_damage": ("§G+5%§! energy weapon damage", "weapon_type_energy_weapon_damage_mult = 0.05"),
    "energy_fire_rate": ("§G+5%§! energy weapon fire rate", "weapon_type_energy_weapon_fire_rate_mult = 0.05"),
    "dimensional_storage": ("§G+5,000§! storage for every resource", "country_resource_max_add = 5000"),
    "food_output": ("§G+5%§! food output from jobs", "planet_jobs_food_produces_mult = 0.05"),
    "core_system_cap": ("§G+5%§! unity", "country_unity_produces_mult = 0.05"),
    "army_damage": ("§G+10%§! army damage", "army_damage_mult = 0.1"),
    "army_health": ("§G+10%§! army health", "army_health = 0.1"),
    "leader_life_span": ("§G+5§! years leader lifespan", "leader_lifespan_add = 5"),
    "strike_craft_damage": ("§G+10%§! strike craft damage", "weapon_type_strike_craft_weapon_damage_mult = 0.10"),
    "strike_craft_fire_rate": ("§G+10%§! strike craft fire rate", "weapon_type_strike_craft_weapon_fire_rate_mult = 0.10"),
    "blokkat_scrap_research": ("§G+5%§! research speed and §G+15%§! Blokkat research speed",
                               "category_blokkats_research_speed_mult = 0.15"),
    "frameworld_outposts": ("§G+10%§! frameworld outpost output", "frameworld_outposts_produces_mult = 0.1"),
    # Effect lives in Giga's giga_tech_eawaf_weapons_repeatable_modifier static modifier; text from Giga's own tooltip.
    "eawaf_weapons": ("§G+10%§! thaumaturgic weapon damage, §R+5%§! thaumaturgic weapon upkeep", None),
}
MEGA_CAP_EFFECT = "§G+1§! build capacity for one megastructure type (one technology per type)"

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
    "mod/common/districts/zz_lfg_district_overrides.txt": [
        # Accommodation District: the regular-empire block that grants its resort workers, then our extra block.
        ("common/districts/00_urban_districts.txt", "district_resort",
         r"^\ttriggered_planet_modifier = \{\n\t\tpotential = \{\n\t\t\texists = owner\n\t\t\towner = \{\n"
         r"\t\t\t\tis_regular_empire = yes\n\t\t\t\}\n\t\t\}\n\t\tmodifier = \{\n"
         r"\t\t\tjob_resort_worker_add = @special_district_jobs\n\t\t\}\n\t\}\n", RESORT_DISTRICT_BLOCK),
    ],
    "mod/common/zones/zz_lfg_zone_overrides.txt": [
        ("common/zones/00_zones.txt", zone, ZONE_SETS_ANCHOR, resort_zone_block(job, amount))
        for zone, job, amount in RESORT_ZONES
    ],
    "mod/common/buildings/zz_lfg_building_overrides.txt": [
        (HOLOMUSEUMS, "xeno_geology_holomuseum", holomuseum_anchor("engineering"), holomuseum_block("engineering")),
        (HOLOMUSEUMS, "aesthetic_wonders_holomuseum", holomuseum_anchor("physics"), holomuseum_block("physics")),
        (HOLOMUSEUMS, "galactic_history_holomuseum", holomuseum_anchor("society"), holomuseum_block("society")),
    ],
    "mod/common/situations/zz_lfg_situation_overrides.txt": [
        ("common/situations/08_machine_age_situations.txt", "situation_synthetic_fertility_digitization",
         r"^\tmonthly_progress = \{\n\t\tbase = 15\n", SYNTH_FERTILITY_BLOCK),
        ("common/situations/08_machine_age_situations.txt", "situation_synthetic_fertility_digitization",
         r"^\t\t\tmachine_age\.3325 #Monthly Progress\n", SYNTH_FERTILITY_UPLOAD),
    ],
    # Shelve edicts: vanilla and Gigastructural repeatables. zz_lfg_ sorts after Giga's zz_giga_ tech files.
    "mod/common/technology/zz_lfg_repeatable_overrides.txt": [
        (src, tech, r"^\tweight_modifier = \{\n", shelve_tech_block(shelve_edict(suffix)))
        for suffix, tech, _area, src, _potential in SHELVE
    ],
    # Events are first-definition-wins (unlike common/), so this file must sort BEFORE vanilla's event files: "00_".
    "mod/events/00_lfg_event_overrides.txt": [
        ("events/machine_age_situation_events_3.txt", EVENT + "machine_age.4400",
         r'^\t\tname = "machine_age\.4400\.c"\n', VIRTUALITY_BLOCK),
    ],
    # Inline scripts can only be replaced as a whole file (same path; this mod loads after Giga). key None = whole file.
    "mod/" + MEGA_CAP_SCRIPT: [
        (GIGA + MEGA_CAP_SCRIPT, None, r"^    weight_modifier = \{\n", shelve_tech_block(MEGA_CAP_EDICT, "        ")),
    ],
}
# Lines written after the header of an override file (event files must declare the namespace of their ids).
PRELUDE = {"mod/events/00_lfg_event_overrides.txt": "\nnamespace = machine_age\n"}
# Localisation overrides: (source loc file, key, text appended to its value). Written to localisation/english/replace/,
# which the game loads over other mods' keys. Generated from the source so the original text stays current.
VIRTUALITY_NOTE = "\\n- §RIndividual machine empires can't take the Virtuality path§! (LFG Traditions)."
LOC_OVERRIDES_FILE = "mod/localisation/english/replace/lfg_origin_overrides_l_english.yml"
LOC_OVERRIDES = [
    (GIGA + "localisation/english/giga_l_english.yml", "origin_tooltip_great_ring_effects", VIRTUALITY_NOTE),
    (GIGA + "localisation/english/giga_alderson_l_english.yml", "origin_alderson_effects", VIRTUALITY_NOTE),
]
LOC_OVERRIDES_KEYS = [key for _src, key, _extra in LOC_OVERRIDES]
# Evolutionary Perfection: value:lfg_num_world_types counts the colonizable planet classes (vanilla + Giga planet_classes
# with `colonizable = yes`) the country owns at least one colony of.
WORLD_TYPES_FILE = "mod/common/script_values/lfg_world_types_values.txt"
SHELVE_EDICTS_FILE = "mod/common/edicts/lfg_shelve_edicts.txt"
SHELVE_LOC_FILE = "mod/localisation/english/lfg_shelve_l_english.yml"


class GenError(RuntimeError):
    pass


def extract_block(text: str, key: str, first: bool = False) -> str:
    """Returns the full text of the top-level `key = { ... }` block (through its closing brace and newline).
    With first=True, the first such block (the key may repeat); otherwise the key must be unique."""
    matches = list(re.finditer(rf"^{re.escape(key)}\s*=\s*\{{", text, re.M))[:1 if first else None]
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


def extract_event(text: str, event_id: str) -> str:
    """Returns the top-level event block (`*_event = { ... }`) whose `id` is event_id."""
    found = []
    for m in re.finditer(r"^([a-z_]*event)\s*=\s*\{", text, re.M):
        block = extract_block(text[m.start():], m.group(1), first=True)
        if re.search(rf"^\tid = {re.escape(event_id)}\s*$", block, re.M):
            found.append(block)
    if len(found) != 1:
        raise GenError(f"expected exactly one event with id {event_id}, found {len(found)}")
    return found[0]


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


def check_shelve_effects(game: Path, giga: Path) -> None:
    """Every shelved tech has an effect text, and its evidence is still in the tech's definition."""
    for suffix, tech, _area, src, _potential in SHELVE:
        if suffix not in SHELVE_EFFECTS:
            raise GenError(f"SHELVE_EFFECTS has no effect text for {suffix} ({tech})")
        evidence = SHELVE_EFFECTS[suffix][1]
        if evidence is not None:
            block = " ".join(extract_block(read_source(src, game, giga), tech).split())
            if evidence not in block:
                raise GenError(f"{tech} no longer contains '{evidence}': update its SHELVE_EFFECTS text")


def generate_shelve_loc() -> str:
    lines = ["\ufeffl_english:\n",
             " # GENERATED by tools/gen_overrides.py from its SHELVE table - do not edit by hand.\n"]
    for suffix, tech, _area, _src, _potential in SHELVE:
        key = "edict_" + shelve_edict(suffix)
        lines.append(f' {key}:0 "Shelve: ${tech}$"\n')
        lines.append(f' {key}_desc:0 "Our researchers stop pursuing §Y${tech}$§!: it is no longer offered as a '
                     f'research option while this edict is active.\\n\\nEach level gives: {SHELVE_EFFECTS[suffix][0]}."\n')
    for area in MEGA_CAP_AREAS:
        key = "edict_" + MEGA_CAP_EDICT.replace("$area$", area)
        name = AREA_NAMES[area]
        lines.append(f' {key}:0 "Shelve: {name} Megastructure Capacity"\n')
        lines.append(f' {key}_desc:0 "Our researchers stop pursuing Gigastructural\'s {area} megastructure capacity '
                     f'repeatables: they are no longer offered as research options while this edict is active.\\n\\n'
                     f'Each level gives: {MEGA_CAP_EFFECT}."\n')
    return "".join(lines)


def generate_loc_overrides(game: Path, giga: Path) -> str:
    lines = ["\ufeffl_english:\n",
             " # GENERATED by tools/gen_overrides.py - do not edit by hand. Source text + an LFG note appended.\n"]
    for src, key, extra in LOC_OVERRIDES:
        hits = re.findall(rf'^[ \t]+{re.escape(key)}:\d*[ \t]*"(.*)"[ \t]*$', read_source(src, game, giga), re.M)
        if len(hits) != 1:
            raise GenError(f"expected exactly one localisation key {key} in {src}, found {len(hits)}")
        lines.append(f' {key}:0 "{hits[0]}{extra}"\n')
    return "".join(lines)


def colonizable_planet_classes(game: Path, giga: Path) -> list[str]:
    classes: set[str] = set()
    for root in (game, giga):
        for path in sorted((root / "common/planet_classes").glob("*.txt")):
            text = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")
            for m in re.finditer(r"^(pc_\w+)\s*=\s*\{", text, re.M):
                block = extract_block(text[m.start():], m.group(1), first=True)
                if re.search(r"^\tcolonizable = yes", block, re.M):
                    classes.add(m.group(1))
    if not classes:
        raise GenError("no colonizable planet classes found in common/planet_classes")
    return sorted(classes)


def generate_world_types(game: Path, giga: Path) -> str:
    lines = [
        "# GENERATED by tools/gen_overrides.py - do not edit by hand.\n",
        "# Evolutionary Perfection: number of colonizable planet classes (vanilla + Gigastructural) the country has a colony on.\n",
        "lfg_num_world_types = {\n",
        "\tbase = 0\n",
    ]
    for pc in colonizable_planet_classes(game, giga):
        lines.append(f"\tmodifier = {{ add = 1 any_owned_planet = {{ is_planet_class = {pc} }} }}\n")
    lines.append("}\n")
    return "".join(lines)


def generate(game: Path, giga: Path = DEFAULT_GIGA) -> dict[str, str]:
    out: dict[str, str] = {}
    for out_path, items in OVERRIDES.items():
        from_giga = any(src.startswith(GIGA) for src, *_ in items)
        sources = f"Stellaris {game_version(game)}" + (f", Gigastructural {giga_version(giga)}" if from_giga else "")
        parts = [
            "# GENERATED by tools/gen_overrides.py - do not edit by hand.\n",
            f"# Verbatim copies of vanilla/Gigastructural definitions ({sources}) with marked LFG additions.\n",
            "# The zz_ file name (or, for inline scripts, the same path in a later-loading mod) makes these replace the originals.\n"
            if not out_path.startswith("mod/events/") else
            "# Events: the first definition of an id wins, so the 00_ file name makes these load before (and replace) vanilla's.\n",
        ]
        parts.append(PRELUDE.get(out_path, ""))
        # Several items may target the same block: copy it once and apply their insertions in order.
        blocks: dict[tuple, str] = {}
        for src, key, anchor, snippet in items:
            if (src, key) not in blocks:
                text = read_source(src, game, giga)
                if key is None:
                    blocks[(src, key)] = text
                elif key.startswith(EVENT):
                    blocks[(src, key)] = extract_event(text, key[len(EVENT):])
                else:
                    blocks[(src, key)] = extract_block(text, key)
            block = blocks[(src, key)]
            hits = [h for h in re.finditer(anchor, block, re.M)]
            if len(hits) != 1:
                raise GenError(f"{key or src}: anchor {anchor!r} matched {len(hits)} times in {src} (expected 1)")
            cut = hits[0].end()
            indent = re.match(r"[ \t]*", snippet).group(0)
            marked = f"{indent}# LFG: added by stellaris-lfg-traditions\n" + snippet
            blocks[(src, key)] = block[:cut] + marked + block[cut:]
        for (src, _key), body in blocks.items():
            parts.append(f"\n# from {src.replace(GIGA, 'Gigastructural ')}\n" + body + ("" if body.endswith("\n") else "\n"))
        out[out_path] = "".join(parts)
    check_shelve_effects(game, giga)
    out[SHELVE_EDICTS_FILE] = generate_shelve_edicts()
    out[SHELVE_LOC_FILE] = generate_shelve_loc()
    out[LOC_OVERRIDES_FILE] = generate_loc_overrides(game, giga)
    out[WORLD_TYPES_FILE] = generate_world_types(game, giga)
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
