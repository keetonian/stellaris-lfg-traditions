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
import gzip
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
\t\t\t\thas_active_tradition = tr_lfg_tourism_hospitality_academies
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
\t\t\t\thas_active_tradition = tr_lfg_tourism_wonders_of_the_galaxy
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
\t\t\t\thas_active_tradition = tr_lfg_tourism_hospitality_academies
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
# Penitence - Prison Industry: +50% of each city specialization's jobs on the penal colony. Penal colonies are regular
# empires on standard (not habitat/ecumenopolis/ring) planets, so only the base regular-empire jobs of each zone count.
# (zone, [(job, amount per zone from the zone's own inline_script parameters)])
PENAL_ZONES = [
    ("zone_industrial", [("foundry", "@scaling_district_2_jobs"), ("artisan", "@scaling_district_2_jobs")]),
    ("zone_foundry", [("foundry", "@scaling_district_1_job")]),
    ("zone_factory", [("artisan", "@scaling_district_1_job")]),
    ("zone_research_unity", [("physicist", "@scaling_district_researchers_4_jobs"),
                             ("biologist", "@scaling_district_researchers_4_jobs"),
                             ("engineer", "@scaling_district_researchers_4_jobs"),
                             ("bureaucrat", "@scaling_district_unity_4_jobs")]),
    ("zone_research", [("physicist", "@scaling_district_3_jobs"), ("biologist", "@scaling_district_3_jobs"),
                       ("engineer", "@scaling_district_3_jobs")]),
    ("zone_research_physics", [("physicist", "@scaling_district_1_job")]),
    ("zone_research_society", [("biologist", "@scaling_district_1_job")]),
    ("zone_research_engineering", [("engineer", "@scaling_district_1_job")]),
    ("zone_unity", [("bureaucrat", "@scaling_district_1_job")]),
    ("zone_unity_spiritualist", [("bureaucrat", "@scaling_district_1_job")]),
    ("zone_fortress", [("soldier", "@scaling_district_1_job")]),
    ("zone_trade", [("trader", "@scaling_district_1_job")]),
]


def penal_zone_block(jobs: list) -> str:
    lines = "".join(f"\t\tjob_{job}_add = {amount}\n" for job, amount in jobs)
    return f"""\ttriggered_district_planet_modifier = {{
\t\tpotential = {{
\t\t\texists = owner
\t\t\towner = {{
\t\t\t\thas_tradition = tr_lfg_penitence_prison_industry
\t\t\t}}
\t\t\thas_modifier = penal_colony
\t\t}}
{lines}\t\tmult = 0.5
\t}}
"""


ZONE_SETS_ANCHOR = r"^\tzone_sets = \{\n(?:\t\t\w+\n)+\t\}\n"


def holomuseum_block(research: str, specimens: str) -> str:
    """Broadcast - Holo-Museums: the museum's base bonuses again (specimen output, and its regular-empire entertainer
    unity/research but not their upkeep), like vanilla's Archaeoengineers blocks in the same building. Kept here, not in
    the tradition, so the tradition's tooltip is just its custom text."""
    return f"""\ttriggered_country_modifier = {{
\t\tpotential = {{
\t\t\texists = owner
\t\t\towner = {{
\t\t\t\thas_active_tradition = tr_lfg_broadcast_holo_museums
\t\t\t}}
\t\t}}
\t\t{specimens}_specimens_produces_mult = @holomuseum_specimen_produces_mult
\t}}
\ttriggered_planet_modifier = {{
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

# Nanite Armada (ap_lfg_nanite_armada): Giga's war moon / planetcraft components (reactors, computers, weapons) check these
# triggers for the ship size, so our hulls are added to them.
GIGA_SHIP_TRIGGERS = GIGA + "common/scripted_triggers/giga_scripted_triggers.txt"

# Nanite harvesters (vanilla cybernetics.5054, every 5 years): two more doublings after vanilla's last (51.2), for every
# harvester. Planets keep nanites_doubled_9 (so vanilla's upkeep value and payouts still see them) and add our
# lfg_nanites_doubled_10 / _11 flags. Step 10 (size >= 30): 51.2 -> 102.4; step 11 (size >= 35): -> 204.8. Each is
# 50%, like vanilla's later steps; the other 50% (and any planet past its last step) falls through to vanilla's payout.
# Step 12 (size >= 40): -> 409.6.
NANITE_EVENTS = "events/machine_age_events_2.txt"
NANITE_STEP_ANCHOR = (r"^\t\t\t\t\t\tset_planet_flag = nanites_doubled_9\n\t\t\t\t\t\tremove_planet_flag = nanites_doubled_8\n"
                      r"\t\t\t\t\t\}\n\t\t\t\t\}\n\t\t\t\}\n")
NANITE_STEP_BLOCK = """\t\t\telse_if = {
\t\t\t\tlimit = {
\t\t\t\t\thas_planet_flag = nanites_doubled_9
\t\t\t\t\tNOT = { has_planet_flag = lfg_nanites_doubled_10 }
\t\t\t\t\tplanet_size >= @lfg_nanite_step_10_size
\t\t\t\t}
\t\t\t\trandom_list = {
\t\t\t\t\t50 = {
\t\t\t\t\t\tnanotech_deposit_nanite_generation = yes
\t\t\t\t\t}
\t\t\t\t\t50 = {
\t\t\t\t\t\tadd_deposit = d_nanite_harvester_deposit_large
\t\t\t\t\t\tadd_deposit = d_nanite_harvester_deposit_large
\t\t\t\t\t\tset_planet_flag = lfg_nanites_doubled_10
\t\t\t\t\t}
\t\t\t\t}
\t\t\t}
\t\t\telse_if = {
\t\t\t\tlimit = {
\t\t\t\t\thas_planet_flag = lfg_nanites_doubled_10
\t\t\t\t\tNOT = { has_planet_flag = lfg_nanites_doubled_11 }
\t\t\t\t\tplanet_size >= @lfg_nanite_step_11_size
\t\t\t\t}
\t\t\t\trandom_list = {
\t\t\t\t\t50 = {
\t\t\t\t\t\tnanotech_deposit_nanite_generation = yes
\t\t\t\t\t}
\t\t\t\t\t50 = {
\t\t\t\t\t\tadd_deposit = d_nanite_harvester_deposit_large
\t\t\t\t\t\tadd_deposit = d_nanite_harvester_deposit_large
\t\t\t\t\t\tadd_deposit = d_nanite_harvester_deposit_large
\t\t\t\t\t\tadd_deposit = d_nanite_harvester_deposit_large
\t\t\t\t\t\tset_planet_flag = lfg_nanites_doubled_11
\t\t\t\t\t}
\t\t\t\t}
\t\t\t}
\t\t\telse_if = {
\t\t\t\tlimit = {
\t\t\t\t\thas_planet_flag = lfg_nanites_doubled_11
\t\t\t\t\tNOT = { has_planet_flag = lfg_nanites_doubled_12 }
\t\t\t\t\tplanet_size >= @lfg_nanite_step_12_size
\t\t\t\t}
\t\t\t\trandom_list = {
\t\t\t\t\t50 = {
\t\t\t\t\t\tnanotech_deposit_nanite_generation = yes
\t\t\t\t\t}
\t\t\t\t\t50 = {
\t\t\t\t\t\twhile = {
\t\t\t\t\t\t\tcount = 8
\t\t\t\t\t\t\tadd_deposit = d_nanite_harvester_deposit_large
\t\t\t\t\t\t}
\t\t\t\t\t\tset_planet_flag = lfg_nanites_doubled_12
\t\t\t\t\t}
\t\t\t\t}
\t\t\t}
"""
# The Nanite Forge origin's own harvester (broken / ancient) keeps its 3-year cycle: vanilla's 5-year doubling skips its
# system (e.g. a Nomad nanotech waystation there), and vanilla's harvester can't be built on the same starbase.
NANITE_SKIP_FORGE_ANCHOR = r"^\ttrigger = \{\n"
NANITE_SKIP_FORGE_BLOCK = """\t\tNOR = {
\t\t\tAND = { exists = starbase starbase = { has_starbase_building = lfg_broken_nanite_harvester } }
\t\t\tAND = { exists = starbase starbase = { has_starbase_building = lfg_ancient_nanite_harvester } }
\t\t}
"""
NANITE_HARVESTER_BAN_BLOCK = """\t\tcustom_tooltip = {
\t\t\tfail_text = lfg_requires_no_ancient_harvester
\t\t\tNOR = {
\t\t\t\thas_starbase_building = lfg_broken_nanite_harvester
\t\t\t\thas_starbase_building = lfg_ancient_nanite_harvester
\t\t\t}
\t\t}
"""
# Harvester removed (vanilla cybernetics.5051): also clear our step flags.
NANITE_CLEANUP_ANCHOR = r"^\t\t\tremove_planet_flag = nanites_doubled_9\n"
NANITE_CLEANUP_BLOCK = ("\t\t\tremove_planet_flag = lfg_nanites_doubled_10\n\t\t\tremove_planet_flag = lfg_nanites_doubled_11\n"
                        "\t\t\tremove_planet_flag = lfg_nanites_doubled_12\n")

# Xenoarchaeology - Expedition Corps: Archaeo-Engineers are the Biologists on a planet with an Archaeostudies Faculty
# (vanilla biologist_is_archaeo_engineer_trigger swaps every Biologist there), so their bonus lives in that building.
ARCHAEO_FACULTY_ANCHOR = r"^\tplanet_modifier = \{\n\t\tplanet_biologists_society_research_produces_add = 0\.25\n\t\}\n"
ARCHAEO_FACULTY_BLOCK = """\ttriggered_planet_modifier = {
\t\tpotential = {
\t\t\texists = owner
\t\t\towner = {
\t\t\t\thas_active_tradition = tr_lfg_xenoarchaeology_expedition_corps
\t\t\t}
\t\t}
\t\tplanet_biologists_produces_mult = 0.25
\t}
"""

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

NANITE_DEPOSITS = "common/deposits/13_machine_age_deposits.txt"
NANITE_DEPOSIT_AMOUNTS = [("d_nanite_harvester_deposit", "0.1"), ("d_nanite_harvester_deposit_regular", "1.6"),
                          ("d_nanite_harvester_deposit_large", "25.6")]

# Same block as vanilla's entertainer job (02_specialist_jobs.txt), inserted before resort_worker's country_modifier
# (after the block that precedes it).
RESORT_WORKER_EXPLOITATION = (
    "\ttriggered_planet_modifier = {\n"
    "\t\tpotential = {\n"
    "\t\t\towner? = {\n"
    "\t\t\t\thas_modifier = exploitation_accord\n"
    "\t\t\t\thas_tradition = tr_lfg_tourism_adopt\n"
    "\t\t\t}\n"
    "\t\t}\n"
    "\t\tplanet_jobs_produces_mult = @accord_exploitation_resources_from_jobs\n"
    "\t}\n"
)

# Storm Sovereignty: cosmic storm penalties that immune Storm Chasers (lfg_storm_immune_country) skip. Each entry is a
# storm type, the modifier line that identifies the penalty block, and who to check ("owner" for planets, fleets and
# ships; "space_owner" for system modifiers); the "not immune" line goes into that block's potential. Bonuses stay.
STORM_TYPES = "common/storm_types/00_storm_types.txt"
# Storm Sovereignty: run lfg_nexus_storm_passes (lfg_storms_effects.txt) whenever a nexus storm leaves a system (vanilla's
# nexus_storm_remove, used by nexus_storm's on_moved and on_finished; system scope), after its aftermath.
STORM_EFFECTS = "common/scripted_effects/cosmic_storms_scripted_effects.txt"
# Nexus Afterglow (lfg_nexus_storm_boon): the particle / celestial aftermaths' per-pop motes / crystals, which live in
# this pop resources inline script (whole file: inline scripts can't be overridden per block).
POP_MISC_PRODUCTION = "common/inline_scripts/pop_resources/pop_misc_production.txt"
NEXUS_BOON_POP_RESOURCE = (
    "produces = {\n\ttrigger = {\n\t\texists = planet\n\t\tplanet = {\n\t\t\thas_modifier = lfg_nexus_storm_boon\n"
    "\t\t}\n\t}\n\t{res} = 0.06\n}}\n\n"
)
STORM_PENALTIES = [
    ("particle_storm", "ships_upkeep_mult = 0\\.5", "owner"),
    ("gravity_storm", "planet_farmers_consumer_goods_upkeep_add = 1", "owner"),
    ("gravity_storm", "planet_farmers_energy_upkeep_add = 1", "owner"),
    ("gravity_storm", "ship_weapon_damage = @gravity_storm_dmg_malus", "owner"),
    ("magnetic_storm", "planet_building_build_speed_mult = -0\\.5", "owner"),
    ("magnetic_storm", "starbase_shipyard_build_speed_mult = -0\\.5", "space_owner"),
    ("magnetic_storm", "stations_upkeep_mult = 1", "owner"),
    ("magnetic_storm", "ships_upkeep_mult = 1", "owner"),
    ("celestial_storm", "planet_enforcers_upkeep_mult = 0\\.5", "owner"),
    ("celestial_storm", "ship_cloaking_strength_add = 10", "owner"),
    ("shroud_storm", "planet_stability_mult = -0\\.2", "owner"),
    ("nexus_storm", "nexus_storm_modifier = 1", "owner"),
]


def storm_penalty_anchor(modifier_line: str) -> str:
    """The `potential = {` line of the block whose first modifier lines include modifier_line (a regex)."""
    return (r"^\t\tpotential = \{\n(?=(?:\t\t\t.*\n)*\t\t\}\n"
            r"(?:\t\t(?:modifier = \{|custom_tooltip = .*)\n|\t\t\tcustom_tooltip = .*\n){0,3}\t\t\t?" + modifier_line + ")")


# Inside a nexus storm, added to nexus_storm: economy (planets) and ship (fleets) bonuses for the Tempest Lodestar's owner
# and for Storm Chasers with Storm Sovereignty (lfg_nexus_storm_bonuses: either); for those Storm Chasers also -25% job
# upkeep ("we have harnessed the storms").
NEXUS_LODESTAR_BONUSES = (
    "\ttriggered_planet_modifier = {\n"
    "\t\tpotential = {\n"
    "\t\t\tis_colony = yes\n"
    "\t\t\towner? = { lfg_nexus_storm_bonuses = yes }\n"
    "\t\t}\n"
    "\t\tplanet_stability_add = @lfg_lodestar_storm_stability\n"
    "\t}\n"
    # Job output, on our colonies inside the nexus storm: +50% from a finished Lodestar, +50% for Storm Chasers with the
    # perk (both: +100%).
    "\ttriggered_planet_modifier = {\n"
    "\t\tpotential = {\n"
    "\t\t\tis_colony = yes\n"
    "\t\t\towner? = { lfg_has_tempest_lodestar = yes }\n"
    "\t\t}\n"
    "\t\tplanet_jobs_produces_mult = @lfg_lodestar_storm_jobs\n"
    "\t}\n"
    "\ttriggered_planet_modifier = {\n"
    "\t\tpotential = {\n"
    "\t\t\tis_colony = yes\n"
    "\t\t\towner? = { lfg_storm_immune_country = yes }\n"
    "\t\t}\n"
    "\t\tplanet_jobs_produces_mult = @lfg_storm_chaser_storm_jobs\n"
    "\t}\n"
    "\ttriggered_planet_modifier = {\n"
    "\t\tpotential = {\n"
    "\t\t\tis_colony = yes\n"
    "\t\t\towner? = { lfg_storm_immune_country = yes }\n"
    "\t\t}\n"
    "\t\tcustom_tooltip = lfg_harnessed_storms_tt\n"
    "\t\tplanet_jobs_upkeep_mult = @lfg_harnessed_storms_upkeep\n"
    "\t}\n"
    "\ttriggered_fleet_modifier = {\n"
    "\t\tpotential = {\n"
    "\t\t\towner? = { lfg_nexus_storm_bonuses = yes }\n"
    "\t\t}\n"
    "\t\tmodifier = {\n"
    "\t\t\tship_fire_rate_mult = @lfg_lodestar_storm_fire_rate\n"
    "\t\t\tship_speed_mult = @lfg_lodestar_storm_speed\n"
    "\t\t\tship_evasion_mult = @lfg_lodestar_storm_evasion\n"
    "\t\t}\n"
    "\t}\n"
    # Storm Chasers' summoned storms (lfg_storms.5 sets these timed fleet flags each month): enemies and neutrals are
    # slowed and get no armour regeneration (vanilla's affect_armor_regen should already stop it; this makes sure).
    "\ttriggered_fleet_modifier = {\n"
    "\t\tpotential = { has_fleet_flag = lfg_storm_lashed }\n"
    "\t\tcustom_tooltip = lfg_storm_lashed_tt\n"
    "\t\tmodifier = {\n"
    "\t\t\tship_speed_mult = @lfg_storm_wrath_speed\n"
    "\t\t\tship_armor_regen_mult = -1\n"
    "\t\t}\n"
    "\t}\n"
    "\ttriggered_fleet_modifier = {\n"
    "\t\tpotential = { has_fleet_flag = lfg_storm_buffeted }\n"
    "\t\tcustom_tooltip = lfg_storm_buffeted_tt\n"
    "\t\tmodifier = {\n"
    "\t\t\tship_speed_mult = @lfg_storm_wrath_speed_half\n"
    "\t\t\tship_armor_regen_mult = -1\n"
    "\t\t}\n"
    "\t}\n"
    "\ttriggered_fleet_modifier = {\n"
    "\t\tpotential = { has_fleet_flag = lfg_storm_favoured }\n"
    "\t\tmodifier = { ship_speed_mult = @lfg_storm_wrath_ally_speed }\n"
    "\t}\n"
)

# Tempest tradition tree: inside any cosmic storm, our colonies (Eye Walkers; the finisher's infrastructure build speed)
# and fleets (Ride the Lightning). Added to
# every storm type, after its lore description line.
STORM_TYPE_KEYS = ["electric_storm", "particle_storm", "gravity_storm", "magnetic_storm", "solar_storm", "celestial_storm",
                   "shroud_storm", "nexus_storm"]
TEMPEST_STORM_BONUSES = (
    "\ttriggered_planet_modifier = {\n"
    "\t\tpotential = {\n"
    "\t\t\tis_colony = yes\n"
    "\t\t\towner? = { has_tradition = tr_lfg_tempest_eye_walkers }\n"
    "\t\t}\n"
    "\t\tplanet_jobs_produces_mult = @lfg_tempest_storm_jobs\n"
    "\t\tplanet_stability_add = @lfg_tempest_storm_stability\n"
    "\t}\n"
    "\ttriggered_planet_modifier = {\n"
    "\t\tpotential = {\n"
    "\t\t\tis_colony = yes\n"
    "\t\t\towner? = { has_tradition = tr_lfg_tempest_finish }\n"
    "\t\t}\n"
    "\t\tplanet_building_build_speed_mult = @lfg_tempest_storm_build_speed\n"
    "\t}\n"
    "\ttriggered_fleet_modifier = {\n"
    "\t\tpotential = {\n"
    "\t\t\towner? = { has_tradition = tr_lfg_tempest_ride_the_lightning }\n"
    "\t\t}\n"
    "\t\tmodifier = {\n"
    "\t\t\tship_fire_rate_mult = @lfg_tempest_storm_fire_rate\n"
    "\t\t\tship_speed_mult = @lfg_tempest_storm_speed\n"
    "\t\t}\n"
    "\t}\n"
)

REPLICATOR_NANITE_UPKEEP = (
    "\t\tupkeep = {\n"
    "\t\t\ttrigger = { owner = { has_origin = origin_lfg_nanite_forge } }\n"
    "\t\t\tnanites = @lfg_nanite_forge_replicator_upkeep\n"
    "\t\t}\n"
)

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
    ] + [
        ("common/zones/00_zones.txt", zone, ZONE_SETS_ANCHOR, penal_zone_block(jobs))
        for zone, jobs in PENAL_ZONES
    ],
    "mod/common/buildings/zz_lfg_building_overrides.txt": [
        (HOLOMUSEUMS, "xeno_geology_holomuseum", holomuseum_anchor("engineering"), holomuseum_block("engineering", "xeno_geology")),
        (HOLOMUSEUMS, "aesthetic_wonders_holomuseum", holomuseum_anchor("physics"), holomuseum_block("physics", "aesthetic_wonder")),
        (HOLOMUSEUMS, "galactic_history_holomuseum", holomuseum_anchor("society"), holomuseum_block("society", "historical_item")),
        ("common/buildings/05_research_buildings.txt", "building_archaeostudies_faculty", ARCHAEO_FACULTY_ANCHOR,
         ARCHAEO_FACULTY_BLOCK),
    ],
    # Nanite Forge origin: +0.5 nanites upkeep per replicator job (per 100 pops working it, like the job's alloys).
    # Tourism adopted: Resort Workers count for the Instrument of Desire's Exploitation accord like Entertainers.
    "mod/common/pop_jobs/zz_lfg_job_overrides.txt": [
        ("common/pop_jobs/04_gestalt_jobs.txt", "replicator", r"^\tresources = \{\n\t\tcategory = planet_pop_assemblers\n",
         REPLICATOR_NANITE_UPKEEP),
        ("common/pop_jobs/02_specialist_jobs.txt", "resort_worker", r"^\t\}\n(?=\s*\tcountry_modifier = \{)",
         RESORT_WORKER_EXPLOITATION),
    ],
    # Nanite harvesters: every harvested nanite deposit yields twice vanilla's (a second, equal produces block; several
    # add up), so a harvester's starting and final amounts double.
    "mod/common/deposits/zz_lfg_deposit_overrides.txt": [
        (NANITE_DEPOSITS, key, rf"^\t\tproduces = \{{\n\t\t\tnanites = {re.escape(amount)}\n\t\t\}}\n",
         f"\t\tproduces = {{\n\t\t\tnanites = {amount}\n\t\t}}\n")
        for key, amount in NANITE_DEPOSIT_AMOUNTS
    ],
    # Storm Sovereignty: storm penalties immune Storm Chasers skip; the Tempest Lodestar's nexus storm bonuses.
    "mod/common/storm_types/zz_lfg_storm_type_overrides.txt": [
        (STORM_TYPES, storm, storm_penalty_anchor(line), f"\t\t\tNOT = {{ {who}? = {{ lfg_storm_immune_country = yes }} }}\n")
        for storm, line, who in STORM_PENALTIES
    ] + [
        (STORM_TYPES, "nexus_storm", r"^\tdescription = nexus_storm_lore_description\n", NEXUS_LODESTAR_BONUSES),
    ] + [
        (STORM_TYPES, storm, rf"^\tdescription = {storm}_lore_description\n", TEMPEST_STORM_BONUSES) for storm in STORM_TYPE_KEYS
    ] + [
        # Vanilla never spawns a nexus storm before the midgame (spawn_weight factor 0), and spawn_random_storm obeys that
        # even with type = nexus_storm: let the Tempest Lodestar's summon (lfg_spawn_nexus_storm) through.
        (STORM_TYPES, "nexus_storm", r"^\t\t\tmid_game_years_passed < 1\n",
         "\t\t\tNOT = { has_global_flag = lfg_summoning_nexus_storm }\n"),
    ],
    "mod/common/scripted_effects/zz_lfg_scripted_effect_overrides.txt": [
        (STORM_EFFECTS, "nexus_storm_remove", r"^\tnexus_storm_apply_aftermath_modifier = yes\n",
         "\tlfg_nexus_storm_passes = yes\n"),
    ],
    "mod/" + POP_MISC_PRODUCTION: [
        (POP_MISC_PRODUCTION, None, r"^\tvolatile_motes = 0\.06\n\}\n\n",
         NEXUS_BOON_POP_RESOURCE.replace("{res}", "volatile_motes").replace("}}", "}")),
        (POP_MISC_PRODUCTION, None, r"^\trare_crystals = 0\.06\n\}\n\n",
         NEXUS_BOON_POP_RESOURCE.replace("{res}", "rare_crystals").replace("}}", "}")),
    ],
    "mod/common/situations/zz_lfg_situation_overrides.txt": [
        ("common/situations/08_machine_age_situations.txt", "situation_synthetic_fertility_digitization",
         r"^\tmonthly_progress = \{\n\t\tbase = 15\n", SYNTH_FERTILITY_BLOCK),
        ("common/situations/08_machine_age_situations.txt", "situation_synthetic_fertility_digitization",
         r"^\t\t\tmachine_age\.3325 #Monthly Progress\n", SYNTH_FERTILITY_UPLOAD),
    ],
    "mod/common/starbase_buildings/zz_lfg_starbase_building_overrides.txt": [
        ("common/starbase_buildings/00_starbase_buildings.txt", "nanite_harvester", r"^\tpossible = \{\n",
         NANITE_HARVESTER_BAN_BLOCK),
    ],
    # Nanite Armada: our hulls use Giga's attack moon / planetcraft components.
    "mod/common/scripted_triggers/zz_lfg_trigger_overrides.txt": [
        (GIGA_SHIP_TRIGGERS, "giga_ship_uses_war_moon_components", r"^\tOR = \{\n", "\t\tis_ship_size = lfg_nanite_war_moon\n"),
        (GIGA_SHIP_TRIGGERS, "giga_ship_uses_war_planet_components", r"^\tOR = \{\n", "\t\tis_ship_size = lfg_nanite_planetcraft\n"),
        (GIGA_SHIP_TRIGGERS, "giga_ship_uses_war_system_components", r"^\tOR = \{\n", "\t\tis_ship_size = lfg_mothership\n"),
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
        (NANITE_EVENTS, EVENT + "cybernetics.5054", NANITE_SKIP_FORGE_ANCHOR, NANITE_SKIP_FORGE_BLOCK),
        (NANITE_EVENTS, EVENT + "cybernetics.5054", NANITE_STEP_ANCHOR, NANITE_STEP_BLOCK),
        (NANITE_EVENTS, EVENT + "cybernetics.5051", NANITE_CLEANUP_ANCHOR, NANITE_CLEANUP_BLOCK),
    ],
    # Inline scripts can only be replaced as a whole file (same path; this mod loads after Giga). key None = whole file.
    "mod/" + MEGA_CAP_SCRIPT: [
        (GIGA + MEGA_CAP_SCRIPT, None, r"^    weight_modifier = \{\n", shelve_tech_block(MEGA_CAP_EDICT, "        ")),
    ],
}
# Lines written after the header of an override file (event files must declare the namespace of their ids).
PRELUDE = {"mod/events/00_lfg_event_overrides.txt": "\nnamespace = machine_age\nnamespace = cybernetics\n"}
# Localisation overrides: (source loc file, key, text appended to its value). Written to localisation/english/replace/,
# which the game loads over other mods' keys. Generated from the source so the original text stays current.
VIRTUALITY_NOTE = "\\n- §RIndividual machine empires can't take the Virtuality path§! (LFG Traditions)."
LOC_OVERRIDES_FILE = "mod/localisation/english/replace/lfg_origin_overrides_l_english.yml"
LOC_OVERRIDES = [
    (GIGA + "localisation/english/giga_l_english.yml", "origin_tooltip_great_ring_effects", VIRTUALITY_NOTE),
    (GIGA + "localisation/english/giga_alderson_l_english.yml", "origin_alderson_effects", VIRTUALITY_NOTE),
]
LOC_OVERRIDES_KEYS = [key for _src, key, _extra in LOC_OVERRIDES]
# Lineage - Every Shore: value:lfg_count_world_types counts the colonizable planet classes (vanilla + Giga planet_classes
# with `colonizable = yes`) the country owns at least one colony of. ~50 any_owned_planet checks, so lfg_lineage.1 runs it
# once a month into a country variable that the tradition reads (value:lfg_num_world_types).
WORLD_TYPES_FILE = "mod/common/script_values/lfg_world_types_values.txt"
SHELVE_EDICTS_FILE = "mod/common/edicts/lfg_shelve_edicts.txt"
# Nanite Cognition Core (common/buildings/lfg_buildings.txt): 50% automation of every specialist / complex drone job
# (vanilla + Giga pop_jobs), as one static modifier with a single tooltip line (the list is ~220 jobs long).
SPECIALIST_AUTOMATION_FILE = "mod/common/static_modifiers/lfg_specialist_automation.txt"
MODIFIERS_SNAPSHOT = REPO / "tools/data/modifiers_4.5.txt.gz"
# Nanite Armada (ap_lfg_nanite_armada): our two hulls reuse Gigastructural's attack moon / planetcraft sections. Copies of
# every section template of Giga's ship size, with our ship size and keys prefixed lfg_nanite_ (keys must be unique).
NANITE_HULLS = [  # (Giga section file, Giga ship size, our ship size)
    (GIGA + "common/section_templates/giga_mooncraft.txt", "giga_war_moon", "lfg_nanite_war_moon"),
    (GIGA + "common/section_templates/giga_planetcraft.txt", "giga_planet_behemoth", "lfg_nanite_planetcraft"),
]
# The hulls whose look is not in a section (Giga puts it on the hull model, which the ship designer doesn't show): their
# "mid" section gets a model holding Giga's weapon locators plus the look (mod/gfx/models/ships/lfg_nanite_hulls.asset,
# lfg_mothership.asset), and the hull model is an invisible frame (engines, explosions).
SECTION_BODIES = {"lfg_nanite_planetcraft": "lfg_nanite_planetcraft_mid_entity", "lfg_mothership": "lfg_mothership_mid_entity"}
NANITE_SECTIONS_FILE = "mod/common/section_templates/lfg_nanite_section_templates.txt"
NANITE_SECTIONS_LOC_FILE = "mod/localisation/english/lfg_nanite_sections_l_english.yml"
# The nanite look (NANITE_ENTITIES_FILE): Giga's moon / planetcraft meshes (and engine particles) with nanite planet
# textures, wrapped in vanilla's grey goo swarm (gray_goo_planet_effect, the Grey Goo world's cloud) on the mesh root.
GIGA_WAR_MOON_ASSET = GIGA + "gfx/models/ships/megastructures/war_moon/giga_war_moon.asset"
GIGA_WAR_PLANET_ASSET = GIGA + "gfx/models/ships/megastructures/war_planet/giga_war_planet.asset"
NANITE_ENTITIES_FILE = "mod/gfx/models/ships/lfg_nanite_celestials.asset"
NANITE_TEXTURES = {  # skin -> (diffuse, normal, specular)
    "grey_goo": ("gray_goo_planet_01_diffuse.dds", "nonormal.dds", "nospec.dds"),
    "machine_shell": ("city_planet_synthetics_01_diffuse.dds", "city_planet_synthetics_01_normal.dds",
                      "city_planet_synthetics_01_specular.dds"),
    "swarm_core": ("ai_01_diffuse.dds", "ai_01_normals.dds", "ai_01_specular.dds"),
}
# Moon: Giga's default look (stern sections) becomes Grey Goo; its optional planet skins (mid sections, behind Giga's
# Aeternite tech) are replaced by our Machine Shell and Swarm Core skins, open to every nanite moon.
NANITE_MOON_DEFAULT_SKIN = ("giga_moon_thrusters_ai_fe", "grey_goo")
NANITE_MOON_EXTRA_SKINS = {"machine_shell": "Machine Shell", "swarm_core": "Swarm Core"}
# Our moons are drawn smaller than Giga's (@war_moon_scale 0.8): next to the planetcraft they looked as big.
NANITE_MOON_SCALE = 0.5
# Mothership (ap_lfg_mothership): Giga's systemcraft sections (slots and weapon locators) for lfg_mothership, whose mid
# section's extra large guns become hangars (with the sternthrusters' own 25: 45 hangars) and every section gets
# MOTHERSHIP_AUX_SLOTS aux slots. Its model is our own (mod/gfx/models/ships/lfg_mothership.asset); the generator only
# makes its core world: Giga's planetcraft mesh in the Swarm Core skin (lfg_mothership_core_entity).
MOTHERSHIP_SECTIONS = (GIGA + "common/section_templates/giga_systemcraft.txt", "giga_systemcraft", "lfg_mothership")
MOTHERSHIP_HANGAR_SLOTS = {"mid"}
# Section names by slot (Giga's systemcraft names otherwise); the bow section with the World Cracker ("W") slot is the
# Disassembler Prow.
MOTHERSHIP_SECTION_NAMES = {
    "bowgun": "Siege Prow",
    "bow": "Siege Driver Battery",
    "mid": "Nanite Hive Bays",
    "stern": "Reshaper Spine",
    "sternthrusters": "Swarm Brood Decks",
    "kugel": "Swarm Heart",
}
MOTHERSHIP_DISASSEMBLER_SECTION_NAME = "Disassembler Prow"
# Aux utility ("A") slots in every Mothership section (Giga's systemcraft: 0-5).
MOTHERSHIP_AUX_SLOTS = 4
MOTHERSHIP_CORE_SKIN = "swarm_core"
MOTHERSHIP_CORE_SCALE = 0.8  # Giga's planetcraft mesh is ~440 wide at scale 1
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
        "# Lineage - Every Shore: number of colonizable planet classes (vanilla + Gigastructural) the country has a colony on.\n",
        "# Expensive (one any_owned_planet per class): only lfg_lineage.1 evaluates it, monthly.\n",
        "lfg_count_world_types = {\n",
        "\tbase = 0\n",
    ]
    for pc in colonizable_planet_classes(game, giga):
        lines.append(f"\tmodifier = {{ add = 1 any_owned_planet = {{ is_planet_class = {pc} }} }}\n")
    lines.append("}\n")
    return "".join(lines)


def specialist_jobs(game: Path, giga: Path) -> list[str]:
    """Jobs whose category is specialist or complex_drone (the gestalt equivalent), vanilla and Gigastructural, that have
    an automation modifier (a few event jobs don't; tools/data/modifiers_4.5.txt.gz lists the game's modifiers)."""
    with gzip.open(MODIFIERS_SNAPSHOT, "rt", encoding="utf-8") as f:
        modifiers = {line.strip() for line in f}
    jobs: set[str] = set()
    for root in (game, giga):
        for path in sorted((root / "common/pop_jobs").glob("*.txt")):
            text = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")
            for m in re.finditer(r"^(\w+)\s*=\s*\{\s*\n\s*category\s*=\s*(?:specialist|complex_drone)\b", text, re.M):
                if f"job_{m.group(1)}_automated_workforce_mult" in modifiers:
                    jobs.add(m.group(1))
    if not jobs:
        raise GenError("no specialist jobs found in common/pop_jobs")
    return sorted(jobs)


SPECIALIST_AUTOMATION_MODIFIERS = [  # (static modifier, automation variable): Cognition Core, its upgrade
    ("lfg_nanite_specialist_automation", "@lfg_nanite_core_automation"),
    ("lfg_nanite_specialist_automation_full", "@lfg_nanite_core_2_automation"),
]


def generate_specialist_automation(game: Path, giga: Path) -> str:
    lines = [
        "# GENERATED by tools/gen_overrides.py - do not edit by hand.\n",
        "# Nanite Cognition Core (50%) and its upgrade, the Nanite Overmind Core (100%): automation of every specialist and\n",
        "# complex drone job (vanilla + Gigastructural). Kept on planets with the active building by lfg_nanite_forge.5\n",
        "# (monthly); one tooltip line instead of one per job.\n",
    ]
    jobs = specialist_jobs(game, giga)
    for name, amount in SPECIALIST_AUTOMATION_MODIFIERS:
        lines += [
            f"{name} = {{\n",
            "\tshow_only_custom_tooltip = yes\n",
            f"\tcustom_tooltip = {name}_tt\n",
            '\ticon = "gfx/interface/icons/planet_modifiers/pm_nanite_world.dds"\n',
            "\ticon_frame = 1\n",
        ]
        lines += [f"\tjob_{job}_automated_workforce_mult = {amount}\n" for job in jobs]
        lines.append("}\n\n")
    return "".join(lines).rstrip("\n") + "\n"


def nanite_sections(game: Path, giga: Path) -> tuple[str, list[tuple[str, str]]]:
    """Section templates for our hulls and their loc ((key, text) pairs): Giga's, with our ship size, prefixed keys and
    the nanite look; Giga's planet-skin moon sections are swapped for ours (built from the first of them)."""
    lines = [
        "# GENERATED by tools/gen_overrides.py - do not edit by hand.\n",
        f"# Nanite Armada hulls: Gigastructural's ({giga_version(giga)}) attack moon and planetcraft section templates, copied\n",
        "# for lfg_nanite_war_moon / lfg_nanite_planetcraft (same slots and utility slots) with the nanite look\n",
        "# (mod/gfx/models/ships/lfg_nanite_celestials.asset).\n",
    ]
    loc: list[tuple[str, str]] = []
    default_entity, default_skin = NANITE_MOON_DEFAULT_SKIN
    for src, giga_size, ours in NANITE_HULLS:
        text = read_source(src, game, giga)
        found, skin_template = 0, None
        for m in re.finditer(r"^ship_section_template\s*=\s*\{", text, re.M):
            block = extract_block(text[m.start():], "ship_section_template", first=True)
            if not re.search(rf"^\tship_size = {giga_size}\s*$", block, re.M):
                continue
            entity = re.search(r'^\tentity = "([^"]+)"', block, re.M)
            if entity and entity.group(1).startswith("giga_moon_thrusters_") and entity.group(1) != default_entity:
                skin_template = skin_template or block
                continue
            key = re.search(r'^\tkey = "([^"]+)"', block, re.M).group(1)
            block = re.sub(rf"^(\tship_size = ){giga_size}\s*$", rf"\g<1>{ours}", block, flags=re.M)
            block = block.replace(f'key = "{key}"', f'key = "lfg_nanite_{key}"', 1)
            block = block.replace(f'entity = "{default_entity}"', f'entity = "lfg_nanite_moon_{default_skin}_entity"')
            block = section_body(block, ours)
            lines.append(f"\n# from {src.replace(GIGA, 'Gigastructural ')}\n" + block)
            loc.append((f"lfg_nanite_{key}", f"${key}$"))
            found += 1
        if not found:
            raise GenError(f"no section templates for {giga_size} in {src}")
        if skin_template:
            for skin, name in NANITE_MOON_EXTRA_SKINS.items():
                block = re.sub(rf"^(\tship_size = ){giga_size}\s*$", rf"\g<1>{ours}", skin_template, flags=re.M)
                block = re.sub(r'^\tkey = "[^"]+"', f'\tkey = "lfg_nanite_moon_{skin}_key"', block, count=1, flags=re.M)
                block = re.sub(r'^\tentity = "[^"]+"', f'\tentity = "lfg_nanite_moon_{skin}_entity"', block, count=1, flags=re.M)
                block = re.sub(r"^\tprerequisites = .*\n", "", block, flags=re.M)
                lines.append(f"\n# nanite skin, slots from Gigastructural's planet-skin sections\n" + block)
                loc.append((f"lfg_nanite_moon_{skin}_key", name))
    src, giga_size, ours = MOTHERSHIP_SECTIONS
    text = read_source(src, game, giga)
    found = 0
    for m in re.finditer(r"^ship_section_template\s*=\s*\{", text, re.M):
        block = extract_block(text[m.start():], "ship_section_template", first=True)
        if not re.search(rf"^\tship_size = {giga_size}\s*$", block, re.M):
            continue
        key = re.search(r'^\tkey = "([^"]+)"', block, re.M).group(1)
        slot = re.search(r'^\tfits_on_slot = "([^"]+)"', block, re.M).group(1)
        block = re.sub(rf"^(\tship_size = ){giga_size}\s*$", rf"\g<1>{ours}", block, flags=re.M)
        block = block.replace(f'key = "{key}"', f'key = "{ours}_{key}"', 1)
        block = re.sub(r"^(\taux_utility_slots = )\d+", rf"\g<1>{MOTHERSHIP_AUX_SLOTS}", block, flags=re.M)
        block = section_body(block, ours)
        name = MOTHERSHIP_SECTION_NAMES.get(slot, f"${key}$")
        if 'template = "invisible_planet_killer_fixed"' in block:
            name = MOTHERSHIP_DISASSEMBLER_SECTION_NAME
        if slot in MOTHERSHIP_HANGAR_SLOTS:
            block = block.replace('template = "invisible_extra_large_fixed"', 'template = "large_strike_craft"')
            block = re.sub(r"^\tai_tags = \{[^}]*\}", "\tai_tags = { carrier }", block, flags=re.M)
        lines.append(f"\n# from {src.replace(GIGA, 'Gigastructural ')}\n" + block)
        loc.append((f"{ours}_{key}", name))
        found += 1
    if not found:
        raise GenError(f"no section templates for {giga_size} in {src}")
    return "".join(lines), loc


def section_body(block: str, ours: str) -> str:
    """A "mid" section of a hull in SECTION_BODIES carries the hull's look (see SECTION_BODIES)."""
    if ours in SECTION_BODIES and re.search(r'^\tfits_on_slot = "?mid"?\s*$', block, re.M):
        block = re.sub(r'^\tentity = "[^"]+"', f'\tentity = "{SECTION_BODIES[ours]}"', block, count=1, flags=re.M)
    return block


def generate_nanite_sections(game: Path, giga: Path) -> str:
    return nanite_sections(game, giga)[0]


def generate_nanite_sections_loc(game: Path, giga: Path) -> str:
    lines = ["\ufeffl_english:\n", " # GENERATED by tools/gen_overrides.py - do not edit by hand. Nanite hull section names.\n"]
    lines += [f' {key}:0 "{text}"\n' for key, text in nanite_sections(game, giga)[1]]
    return "".join(lines)


def extract_entity(text: str, name: str) -> str:
    """The `entity = { ... }` block (from a .asset file) whose name is `name`."""
    m = re.search(rf'^\tname = "{re.escape(name)}"', text, re.M)
    if not m:
        raise GenError(f"entity {name} not found")
    start = text.rfind("\nentity = {", 0, m.start()) + 1
    return extract_block(text[start:], "entity", first=True)


def nanite_entity(block: str, name: str, skin: str, swarm: str | None) -> str:
    diffuse, normal, specular = NANITE_TEXTURES[skin]
    block = re.sub(r'^(\tname = )"[^"]+"', rf'\g<1>"{name}"', block, count=1, flags=re.M)
    block = re.sub(r'(texture_diffuse = )"[^"]+"', rf'\g<1>"{diffuse}"', block)
    block = re.sub(r'(texture_normal = )"[^"]+"', rf'\g<1>"{normal}"', block)
    block = re.sub(r'(texture_specular = )"[^"]+"', rf'\g<1>"{specular}"', block)
    if swarm is None:
        return block
    return re.sub(r"^\tgame_data = \{", f'\tattach = {{ root = "{swarm}" }}\n\n\tgame_data = {{', block, count=1, flags=re.M)


NANITE_SWARM_ENTITIES = """
# The swarm: vanilla's grey goo world cloud particle on a locator, attached to the hull's root node. Its size follows
# the scale; change @lfg_nanite_swarm_*_scale to fit it around the hull.
@lfg_nanite_swarm_planet_scale = 5
@lfg_nanite_swarm_mothership_scale = 15
"""
for _hull in ("planet", "mothership"):
    NANITE_SWARM_ENTITIES += f"""
entity = {{
	name = "lfg_nanite_swarm_{_hull}_entity"
	pdxmesh = "locator_mesh"
	cull_radius = 10000
	scale = @lfg_nanite_swarm_{_hull}_scale
	locator = {{ name = "swarm" position = {{ 0 0 0 }} }}
	default_state = "idle"
	state = {{ name = "idle" state_time = 5
		start_event = {{ node = "swarm" particle = "gray_goo_planet_effect" keep_particle = yes trigger_once = yes }}
	}}
	state = {{ name = "moving" state_time = 5
		start_event = {{ node = "swarm" particle = "gray_goo_planet_effect" keep_particle = yes trigger_once = yes }}
	}}
}}
"""


def generate_nanite_entities(game: Path, giga: Path) -> str:
    moon = read_source(GIGA_WAR_MOON_ASSET, game, giga)
    planet = read_source(GIGA_WAR_PLANET_ASSET, game, giga)
    moon_template = extract_entity(moon, NANITE_MOON_DEFAULT_SKIN[0])
    parts = [
        "# GENERATED by tools/gen_overrides.py - do not edit by hand.\n",
        f"# Nanite Armada hulls' look: Gigastructural's ({giga_version(giga)}) moon / planetcraft entities with nanite planet\n",
        "# textures and a grey goo swarm. Moon skins are picked through the hull sections; the planetcraft has one look.\n",
        re.search(r"^@war_moon_scale = .*\n", moon, re.M).group(0),
        re.search(r"^@war_planet_scale = .*\n", planet, re.M).group(0),
        NANITE_SWARM_ENTITIES,
    ]
    # No swarm on the moon (in game it showed as a dark blob hiding the moon); its escort ring of nanite ships instead
    # (lfg_nanite_moon_escort_entity in lfg_nanite_hulls.asset). The skins are the moon's stern sections.
    parts.append(f"@lfg_nanite_moon_scale = {NANITE_MOON_SCALE}\n")
    for skin in [NANITE_MOON_DEFAULT_SKIN[1], *NANITE_MOON_EXTRA_SKINS]:
        moon_skin = nanite_entity(moon_template, f"lfg_nanite_moon_{skin}_entity", skin, "lfg_nanite_moon_escort_entity")
        parts.append("\n" + re.sub(r"^(\tscale = )@war_moon_scale\b", r"\g<1>@lfg_nanite_moon_scale", moon_skin,
                                    count=1, flags=re.M))
    # Planetcraft: the grey goo world alone, scale 1 (it sits in the mid section, under the hull frame's scale); the rest
    # of its look is lfg_nanite_planetcraft_mid_entity in lfg_nanite_hulls.asset.
    body = nanite_entity(extract_entity(planet, "synthetics_01_war_planet_complete_entity"),
                         "lfg_nanite_planetcraft_body_entity", "grey_goo", None)
    parts.append("\n" + re.sub(r"^(\tscale = )@war_planet_scale", r"\g<1>1", body, count=1, flags=re.M))
    # Mothership: only its core world (the model around it is mod/gfx/models/ships/lfg_mothership.asset).
    core = nanite_entity(extract_entity(planet, "synthetics_01_war_planet_complete_entity"), "lfg_mothership_core_entity",
                         MOTHERSHIP_CORE_SKIN, None)
    core = re.sub(r"^(\tscale = )@war_planet_scale", r"\g<1>@lfg_mothership_core_scale", core, count=1, flags=re.M)
    parts.append(f"\n# The Mothership's core world\n@lfg_mothership_core_scale = {MOTHERSHIP_CORE_SCALE}\n" + core)
    return "".join(parts)


# ---- Here Be Dragons: growing drakes (ap_lfg_legendary_dragons; events/lfg_dragons_events.txt) ----
# The origin's Baby Drakes (vanilla space_dragon_origin_baby) become our step 0 (lfg_drake_0) at once, then grow one step
# every 4 years (DRAKE_STEP_YEARS; lfg_dragons.1 counts 48 months): durability (hull, plus
# armour from the Juvenile stage) and weapon damage x1.75 per step up to the Elder (step 11, about a Gigastructural
# Planetcraft), then, for the one Legendary Dragon, x1.5 per step up to step 24 (~917M, under the engine's ~2 billion).
# The model grows by the 1/4 power of that (capped Legendary: ~1,070 long, a systemcraft +12%). Food upkeep x1.45 per
# step to the Elder (2,477), then x1.292 per Legendary step (~69,000 at step 24). One ship size, section, design and
# model per step, copied from vanilla's baby drake; the designs carry the Dragon's Breath (LFG_DRAKE_BREATH,
# common/component_templates/lfg_components.txt) and six of vanilla's twelve smaller weapons (DRAKE_KEEP_SLOTS).
DRAKE_SOURCES = {
    "weapons": "common/component_templates/00_leviathans_weapons.txt",
    "weapon_stats": "common/component_templates/weapon_components.csv",
    "size": "common/ship_sizes/11_leviathans.txt",
    "section": "common/section_templates/leviathans.txt",
    "design": "common/global_ship_designs/leviathans_designs.txt",
    "asset": "gfx/models/ships/guardians/space_dragon/guardian_01_space_dragon.asset",
}
DRAKE_BABY_SIZE = "space_dragon_origin_baby"
DRAKE_ELDER_STEP = 11
DRAKE_STEP_YEARS = 4  # keep in step with lfg_dragons.1 (48 months)
DRAKE_MAX_STEP = 24
DRAKE_BASE_HP = 8500  # 10,000 at first, -15%
DRAKE_GROWTH, DRAKE_LEGEND_GROWTH = 1.75, 1.5  # size (model) growth
# Legendary durability grows slower than its size: x1.35 a step (cap ~230M, ~1.8x the Mothership's 127M).
DRAKE_LEGEND_DURABILITY_GROWTH = 1.35
# Weapon damage has its own curve: half the durability growth up to the Elder, then x1.3 a Legendary step (durability:
# x1.5), so a capped Legendary hits ~x7,100 a baby's breath, not x91,750.
DRAKE_DAMAGE_FACTOR, DRAKE_LEGEND_DAMAGE_GROWTH = 0.32, 1.3  # 0.5 at first, -20%, -20%
DRAKE_FOOD, DRAKE_FOOD_GROWTH, DRAKE_LEGEND_FOOD_GROWTH = 41.58, 1.45, 1.292  # 48 at first, -25%, then +10%, then +5% at every step
DRAKE_BREATH = "LFG_DRAKE_BREATH"
# Vanilla weapon slots kept beside the breath: four claw / wing strikes (our LFG_DRAKE_CLAW_<step>: vanilla's
# DRAGON_SECONDARY_WEAPON_ICE, 100-150 every ~15 days, times the step's growth) and two point defence
# (DRAGON_TERTIARY_WEAPON_ICE, unchanged): steady fire between breaths.
DRAKE_KEEP_SLOTS = {"SECONDARY_GUN_01", "SECONDARY_GUN_02", "SECONDARY_GUN_03", "SECONDARY_GUN_04",
                    "TERTIARY_GUN_01", "TERTIARY_GUN_02"}
# Durability split at every step: mostly hull and armour, a token shield; plus damage reduction and living regeneration.
DRAKE_HULL_SHARE, DRAKE_ARMOR_SHARE, DRAKE_SHIELD_SHARE = 0.62, 0.108, 0.002  # shields: 2% at first, -90%; armour: 0.48, a quarter moved to hull, then -70%
DRAKE_DAMAGE_REDUCTION = 0  # removed (was 25%, then 10%)
DRAKE_REGEN = 0  # bonus hull / armour regeneration removed (was 25%, then 0.5%)
# The Legendary Dragon's hull grows extra: x1 at the Elder's step, rising evenly to x2 at step 24 (~917M hull, under the
# ~2.1 billion the game can hold).
DRAKE_LEGEND_HULL_BONUS = 0.0  # was 1.0 (x2 hull at step 24); dropped with DRAKE_LEGEND_DURABILITY_GROWTH
# Speeding growth up (ap_lfg_legendary_dragons + tech_lfg_draconic_feast): a Feast costs DRAKE_FEAST_MONTHS of the drake's
# current food upkeep for one step (48 months) of growth; a Tribute of pops costs DRAKE_TRIBUTE_PER_STEP x its step (x3 for
# the Legendary Dragon) hundred pops.
DRAKE_FEAST_MONTHS = 60
DRAKE_TRIBUTE_PER_STEP, DRAKE_TRIBUTE_LEGEND_MULT = 1, 3
DRAKE_RANGE_PER_STEP = 0.05  # weapon range per growth step: +120% at step 24 (the breath: 320 -> ~704)
DRAKE_STAGES = [(3, "Baby Drake"), (6, "Juvenile Dragon"), (10, "Dragon"), (11, "Elder Dragon"), (DRAKE_MAX_STEP, "Legendary Dragon")]
# The Dragon's Breath, one per step (its damage and splash baked in: a ship_weapon_damage modifier on the ship size
# didn't raise its damage in game): base damage and splash, times the step's growth.
DRAKE_BREATH_DAMAGE = (5000, 9000)
DRAKE_BREATH_SPLASH = (500, 1620)  # 2,500-8,100 at first, -60%, -50%
DRAKE_SPLASH_RADIUS, DRAKE_LEGEND_SPLASH_RADIUS_STEP = 120, 10  # +10 a Legendary step: 250 at step 24
DRAKE_BREATH_TEMPLATE = """weapon_component_template = {{
	key = "{key}"
	size = large
	icon = "GFX_ship_part_energy_lance_2"
	icon_frame = 1
	type = instant
	prio_projectile = yes

	damage = {{ min = {dmin} max = {dmax} }}
	windup = {{ min = 5 max = 15 }}
	total_fire_time = @lfg_drake_breath_cooldown
	range = @lfg_drake_breath_range
	accuracy = 0.95
	power = 0
	hull_damage = 1.5	# 150% against hull
	armor_penetration = 0.25
	armor_damage = 1.25
	shield_penetration = 0.25
	shield_damage = 1.25
	tracking = 1.0

	firing_arc = 30.0
	min_range = 0
	hidden = yes

	on_hit = {{
		hidden_effect = {{
			solar_system = {{
				every_ship_in_system = {{
					limit = {{
						NOT = {{ is_same_value = root }}
						controller = {{ is_hostile = from.controller }}
						distance = {{
							source = root
							max_distance <= {radius}
							same_solar_system = yes
						}}
					}}
					set_variable_to_random_value = {{
						which = lfg_drake_splash_damage
						min = {smin}
						max = {smax}
						rounded = yes
					}}
					damage_ship = {{
						amount = lfg_drake_splash_damage
						attacker = from
					}}
					clear_variable = lfg_drake_splash_damage
				}}
			}}
		}}
		custom_tooltip = {key}_ON_HIT_TT
	}}

	projectile_gfx = "lfg_drake_breath"
	tags = {{
		weapon_type_energy
		weapon_type_space_fauna
		l_slot
	}}
}}
"""
# The claws: vanilla's secondary ice weapon (its stats from weapon_components.csv), damage times the step's growth.
DRAKE_CLAW_SOURCE = "DRAGON_SECONDARY_WEAPON_ICE"
DRAKE_CLAW_DAMAGE_FACTOR = 0.5  # on top of the damage curve: half the claws' first damage
DRAKE_FILES = {
    "size": "mod/common/ship_sizes/lfg_drake_ship_sizes.txt",
    "section": "mod/common/section_templates/lfg_drake_section_templates.txt",
    "design": "mod/common/global_ship_designs/lfg_drake_designs.txt",
    "asset": "mod/gfx/models/ships/lfg_drakes.asset",
    "effects": "mod/common/scripted_effects/lfg_drake_steps_effects.txt",
    "triggers": "mod/common/scripted_triggers/lfg_drake_steps_triggers.txt",
    "loc": "mod/localisation/english/lfg_drakes_l_english.yml",
    "weapons": "mod/common/component_templates/lfg_drake_weapons.txt",
}


def drake_steps() -> list[tuple[str, int, bool]]:
    """(ship size key, step, legendary) for our sizes: steps 1..11, the Legendary Elder, then 12..24."""
    steps = [(f"lfg_drake_{n}", n, False) for n in range(0, DRAKE_ELDER_STEP + 1)]
    steps.append((f"lfg_drake_{DRAKE_ELDER_STEP}_legendary", DRAKE_ELDER_STEP, True))
    return steps + [(f"lfg_drake_{n}", n, True) for n in range(DRAKE_ELDER_STEP + 1, DRAKE_MAX_STEP + 1)]


def drake_stats(n: int) -> dict:
    growth = DRAKE_GROWTH ** min(n, DRAKE_ELDER_STEP) * DRAKE_LEGEND_GROWTH ** max(0, n - DRAKE_ELDER_STEP)
    food = DRAKE_FOOD * DRAKE_FOOD_GROWTH ** min(n, DRAKE_ELDER_STEP) * DRAKE_LEGEND_FOOD_GROWTH ** max(0, n - DRAKE_ELDER_STEP)
    total = DRAKE_BASE_HP * DRAKE_GROWTH ** min(n, DRAKE_ELDER_STEP) * DRAKE_LEGEND_DURABILITY_GROWTH ** max(0, n - DRAKE_ELDER_STEP)
    armor, shield = total * DRAKE_ARMOR_SHARE, total * DRAKE_SHIELD_SHARE
    hull = total * DRAKE_HULL_SHARE * (1 + DRAKE_LEGEND_HULL_BONUS * max(0, n - DRAKE_ELDER_STEP) / (DRAKE_MAX_STEP - DRAKE_ELDER_STEP))
    damage = DRAKE_DAMAGE_FACTOR * DRAKE_GROWTH ** min(n, DRAKE_ELDER_STEP) * DRAKE_LEGEND_DAMAGE_GROWTH ** max(0, n - DRAKE_ELDER_STEP)
    return {"growth": growth, "damage": damage, "hp": round(hull), "armor": round(armor), "shield": round(shield),
            "food": round(food), "length": growth ** 0.25}


def drake_feast_cost(n: int) -> int:
    return drake_stats(n)["food"] * DRAKE_FEAST_MONTHS


def drake_tribute(n: int, legendary: bool) -> int:
    """Hundreds of pops a Tribute costs."""
    return max(1, n) * DRAKE_TRIBUTE_PER_STEP * (DRAKE_TRIBUTE_LEGEND_MULT if legendary else 1)


def drake_stage(n: int, legendary: bool) -> str:
    if legendary:
        return DRAKE_STAGES[-1][1]
    return next(name for last, name in DRAKE_STAGES if n <= last)


def drake_design(key: str) -> str:
    return "NAME_LFG_" + key.title().replace("Lfg_", "")


def generate_drakes(game: Path) -> dict[str, str]:
    header = ("# GENERATED by tools/gen_overrides.py - do not edit by hand.\n"
              f"# Here Be Dragons' growing drakes, from vanilla's baby drake (Stellaris {game_version(game)}).\n")
    asset = read_source(DRAKE_SOURCES["asset"], game, DEFAULT_GIGA)
    section = None
    text = read_source(DRAKE_SOURCES["section"], game, DEFAULT_GIGA)
    for m in re.finditer(r"^ship_section_template\s*=\s*\{", text, re.M):
        block = extract_block(text[m.start():], "ship_section_template", first=True)
        if re.search(rf"^\tship_size = {DRAKE_BABY_SIZE}\s*$", block, re.M):
            section = block
    design = None
    text = read_source(DRAKE_SOURCES["design"], game, DEFAULT_GIGA)
    for m in re.finditer(r"^ship_design\s*=\s*\{", text, re.M):
        block = extract_block(text[m.start():], "ship_design", first=True)
        if re.search(rf"^\tship_size = {DRAKE_BABY_SIZE}\s*$", block, re.M):
            design = block
    if section is None or design is None:
        raise GenError(f"no section template / design for {DRAKE_BABY_SIZE}")
    root_entity = extract_entity(asset, "aquatic_dragon_baby_entity")
    body_entity = extract_entity(asset, "aquatic_dragon_baby_section_entity")
    base_scale = float(re.search(r"^\tscale = ([\d.]+)", body_entity, re.M).group(1))
    size_block = extract_block(read_source(DRAKE_SOURCES["size"], game, DEFAULT_GIGA), DRAKE_BABY_SIZE)
    base_radius = float(re.search(r"^\tcollision_radius = ([\d.]+)", size_block, re.M).group(1))
    base_size = float(re.search(r"^\tsize_multiplier = ([\d.]+)", size_block, re.M).group(1))
    speed = re.search(r"^\tmax_speed = (\S+)", size_block, re.M).group(1)

    # The claws' stats: vanilla's CSV row (key;cost;power;min_damage;max_damage;hull;shield;shield_pen;armor;armor_pen;
    # min_windup;max_windup;cooldown;range;accuracy;tracking;...) and its txt block (look, tags).
    stats = None
    for line in read_source(DRAKE_SOURCES["weapon_stats"], game, DEFAULT_GIGA).splitlines():
        if line.startswith(DRAKE_CLAW_SOURCE + ";"):
            stats = [float(v) for v in line.split(";")[1:16]]
    text = read_source(DRAKE_SOURCES["weapons"], game, DEFAULT_GIGA)
    claw = None
    for m in re.finditer(r"^weapon_component_template\s*=\s*\{", text, re.M):
        block = extract_block(text[m.start():], "weapon_component_template", first=True)
        if f'key = "{DRAKE_CLAW_SOURCE}"' in block:
            claw = block
    if stats is None or claw is None:
        raise GenError(f"{DRAKE_CLAW_SOURCE} not found in {DRAKE_SOURCES['weapon_stats']} / {DRAKE_SOURCES['weapons']}")
    (_cost, _power, dmin, dmax, hull, shield, shield_pen, armor, armor_pen, wmin, wmax, cooldown, rng, acc, track) = stats
    weapons = [header, "# The Dragon's Breath and the claws, one of each per growth step, damage times the step's growth.\n"]

    sizes, sections, designs, entities, effects, loc = [header], [header], [header], [header], [header], []
    for key, n, legendary in drake_steps():
        s = drake_stats(n)
        stage = drake_stage(n, legendary)
        defense_lines = "".join(f"\t\t{k} = {v}\n" for k, v in (
            ("ship_damage_reduction_mult", DRAKE_DAMAGE_REDUCTION), ("ship_hull_regen_add_perc", DRAKE_REGEN),
            ("ship_armor_regen_add_perc", DRAKE_REGEN)) if v)
        sizes.append(f"""
# Step {n} ({n * DRAKE_STEP_YEARS} years): {stage}, durability {s['hp'] + s['armor'] + s['shield']:,}, damage x{s['growth']:,.1f}, model x{s['length']:.2f}
{key} = {{
	entity = "{key}_entity"
	is_space_object = yes
	graphical_culture = no
	can_be_inspected = no
	max_speed = {speed}
	acceleration = 0.8
	rotation_speed = 0.8
	collision_radius = {base_radius * s['length']:.1f}
	modifier = {{
		ship_evasion_add = 25
		ship_armor_add = {s['armor']}
		ship_shield_add = {s['shield']}
{defense_lines}		ship_weapon_range_mult = {DRAKE_RANGE_PER_STEP * n:.2f}
	}}
	max_hitpoints = {s['hp']}
	size_multiplier = {round(base_size * s['length'])}
	map_counter_icon = ship_counter_32
	icon = ship_size_space_monster
	fleet_slot_size = 8
	section_slots = {{ "mid" = {{ locator = "part1" }} }}
	num_target_locators = 0
	is_space_station = no
	class = shipclass_military
	is_designable = no
	components_add_to_cost = no
	resources = {{
		category = ships
		upkeep = {{
			food = {s['food']}
		}}
	}}
}}
""")
        block = section.replace(f'key = "{DRAKE_BABY_SIZE}_key"', f'key = "{key}_key"', 1)
        block = re.sub(rf"^(\tship_size = ){DRAKE_BABY_SIZE}\s*$", rf"\g<1>{key}", block, flags=re.M)
        block = re.sub(r'^\tentity = "aquatic_dragon_baby_section_entity"', f'\tentity = "{key}_section_entity"', block, flags=re.M)
        sections.append("\n" + block)
        block = re.sub(r'^\tname = "[^"]+"', f'\tname = "{drake_design(key)}"', design, count=1, flags=re.M)
        block = re.sub(rf"^(\tship_size = ){DRAKE_BABY_SIZE}\s*$", rf"\g<1>{key}", block, flags=re.M)
        block = block.replace(f'template = "{DRAKE_BABY_SIZE}_key"', f'template = "{key}_key"')
        # The breath in vanilla's primary slot, plus a few of vanilla's smaller ice attacks (DRAKE_KEEP_SLOTS: claws and
        # wings, two point defence); the other slots left empty.
        block = re.sub(r'\t\tcomponent = \{\n\t\t\tslot = "((?:SECONDARY|TERTIARY)_GUN_\d+)"\n\t\t\ttemplate = "[^"]+"\n\t\t\}\n',
                       lambda m: m.group(0) if m.group(1) in DRAKE_KEEP_SLOTS else "", block)
        block = block.replace('template = "DRAGON_WEAPON_ICE"', f'template = "{DRAKE_BREATH}_{n}"')
        block = block.replace(f'template = "{DRAKE_CLAW_SOURCE}"', f'template = "LFG_DRAKE_CLAW_{n}"')
        if f"{DRAKE_BREATH}_{n}" not in block:
            raise GenError(f"{DRAKE_BABY_SIZE}'s design changed: can't swap its weapons for {DRAKE_BREATH}")
        designs.append("\n" + block)
        root = root_entity.replace('name = "aquatic_dragon_baby_entity"', f'name = "{key}_entity"', 1)
        root = re.sub(r"^\tcull_radius = [\d.]+", f"\tcull_radius = {10 * s['length']:.1f}", root, flags=re.M)
        body = body_entity.replace('name = "aquatic_dragon_baby_section_entity"', f'name = "{key}_section_entity"', 1)
        body = re.sub(r"^\tscale = [\d.]+", f"\tscale = {base_scale * s['length']:.3f}", body, count=1, flags=re.M)
        entities.append("\n" + root + "\n" + body)
        loc += [(key, stage), (f"{key}_plural", stage + "s"), (drake_design(key), stage)]
        if not legendary or n != DRAKE_ELDER_STEP:  # the Legendary Elder shares step 11's weapons
            g = s["damage"]
            bkey = f"{DRAKE_BREATH}_{n}"
            radius = DRAKE_SPLASH_RADIUS + DRAKE_LEGEND_SPLASH_RADIUS_STEP * max(0, n - DRAKE_ELDER_STEP)
            weapons.append(f"\n# Step {n}: damage x{g:,.2f}\n" + DRAKE_BREATH_TEMPLATE.format(
                key=bkey, dmin=round(DRAKE_BREATH_DAMAGE[0] * g), dmax=round(DRAKE_BREATH_DAMAGE[1] * g),
                smin=round(DRAKE_BREATH_SPLASH[0] * g), smax=round(DRAKE_BREATH_SPLASH[1] * g), radius=radius))
            stat_lines = (f"\tdamage = {{ min = {round(dmin * g * DRAKE_CLAW_DAMAGE_FACTOR)} max = {round(dmax * g * DRAKE_CLAW_DAMAGE_FACTOR)} }}\n"
                          f"\twindup = {{ min = {wmin:g} max = {wmax:g} }}\n\ttotal_fire_time = {cooldown:g}\n"
                          f"\trange = {rng:g}\n\taccuracy = {acc:g}\n\ttracking = {track:g}\n\tpower = 0\n"
                          f"\thull_damage = {hull:g}\n\tshield_damage = {shield:g}\n\tshield_penetration = {shield_pen:g}\n"
                          f"\tarmor_damage = {armor:g}\n\tarmor_penetration = {armor_pen:g}\n")
            block = claw.replace(f'key = "{DRAKE_CLAW_SOURCE}"', f'key = "LFG_DRAKE_CLAW_{n}"', 1)
            block = block.replace("\ttype = instant\n", "\ttype = instant\n" + stat_lines, 1)
            weapons.append("\n" + block)
            loc += [(bkey, "Dragon's Breath"),
                    (f"{bkey}_DESC", "A torrent of frozen fire that grows with the dragon."),
                    (f"{bkey}_ON_HIT_TT", f"§HSplash:§! every other hostile ship within §Y{radius}§! of the target takes "
                                          f"§R{round(DRAKE_BREATH_SPLASH[0] * g):,}-{round(DRAKE_BREATH_SPLASH[1] * g):,}§! damage."),
                    (f"LFG_DRAKE_CLAW_{n}", "Dragon Claws"),
                    (f"LFG_DRAKE_CLAW_{n}_DESC", "Ice-sheathed claws and wings, as big as the dragon.")]

    # Move a drake (ship scope, ship variable lfg_drake_step already set to its new step) onto that step's design; if the
    # game won't switch a ship to another ship size, replace it with a new ship of that design in the same fleet.
    effects.append("\n# Ship scope: switch to the design of ship variable lfg_drake_step (and the Legendary Elder's with flag\n"
                   "# lfg_legendary_dragon), and store its growth (ship variable lfg_drake_growth: the Dragon's Breath splash\n"
                   "# reads it). If the ship size didn't change, it's replaced (lfg_drake_replace).\n"
                   "lfg_drake_set_design = {\n")
    first = True
    for key, n, legendary in drake_steps():
        cond = f"check_variable = {{ which = lfg_drake_step value = {n} }}"
        if n == DRAKE_ELDER_STEP:
            cond += " has_ship_flag = lfg_legendary_dragon" if legendary else " NOT = { has_ship_flag = lfg_legendary_dragon }"
        effects.append(f"\t{'if' if first else 'else_if'} = {{\n\t\tlimit = {{ {cond} }}\n"
                       f"\t\tset_variable = {{ which = lfg_drake_growth value = {drake_stats(n)['growth']:.2f} }}\n"
                       f"\t\tset_variable = {{ which = lfg_drake_feast_cost value = {drake_feast_cost(n)} }}\n"
                       f"\t\tset_variable = {{ which = lfg_drake_tribute value = {drake_tribute(n, legendary) * 100} }}\n"
                       f"\t\tset_ship_design = {{ design = \"{drake_design(key)}\" }}\n"
                       f"\t\tif = {{\n\t\t\tlimit = {{ NOT = {{ is_ship_size = {key} }} }}\n"
                       f"\t\t\tlfg_drake_replace = {{ DESIGN = \"{drake_design(key)}\" }}\n\t\t}}\n\t}}\n")
        first = False
    effects.append("}\n")
    # Feast and Tribute: per step, as literal numbers (a stockpile can't be compared with a variable).
    def step_cond(n, legendary):
        cond = f"check_variable = {{ which = lfg_drake_step value = {n} }}"
        if n == DRAKE_ELDER_STEP:
            cond += " has_ship_flag = lfg_legendary_dragon" if legendary else " NOT = { has_ship_flag = lfg_legendary_dragon }"
        elif n > DRAKE_ELDER_STEP:
            cond += " has_ship_flag = lfg_legendary_dragon"
        return cond
    afford, pay, tribute = [], [], []
    for key, n, legendary in drake_steps():
        c = step_cond(n, legendary)
        afford.append(f"\t\tAND = {{ {c} owner = {{ resource_stockpile_compare = {{ resource = food value >= {drake_feast_cost(n)} }} }} }}\n")
        pay.append(f"\t{'if' if not pay else 'else_if'} = {{ limit = {{ {c} }} owner = {{ add_resource = {{ food = -{drake_feast_cost(n)} }} }} }}\n")
        tribute.append(f"\t\tAND = {{ {c} owner = {{ count_owned_pop_amount = {{ count >= {drake_tribute(n, legendary) * 100} }} }} }}\n")
    effects.append("\n# Ship scope: pay its Feast (DRAKE_FEAST_MONTHS of its current food upkeep).\nlfg_drake_pay_feast = {\n"
                   + "".join(pay) + "}\n")
    sizes_list = "\n".join(f"\t\tis_ship_size = {key}" for key, _n, _l in drake_steps())
    triggers = header + "\n# Ship scope: its owner can pay its Feast.\nlfg_drake_can_afford_feast = {\n\tOR = {\n" + "".join(afford) + \
        "\t}\n}\n\n# Ship scope: its owner has the pops for its Tribute.\nlfg_drake_can_pay_tribute = {\n\tOR = {\n" + \
        "".join(tribute) + "\t}\n}\n" + f"""
# Ship scope: one of the origin's drakes (vanilla's Baby Drake, or one of our growth steps).
lfg_is_drake = {{
	OR = {{
		is_ship_size = {DRAKE_BABY_SIZE}
{sizes_list}
	}}
}}
"""
    loc_text = "﻿l_english:\n # GENERATED by tools/gen_overrides.py - do not edit by hand. Growing drake stage names.\n" + \
        "".join(f' {k}:0 "{v}"\n' for k, v in loc)
    return {DRAKE_FILES["size"]: "".join(sizes), DRAKE_FILES["section"]: "".join(sections),
            DRAKE_FILES["design"]: "".join(designs), DRAKE_FILES["asset"]: "".join(entities),
            DRAKE_FILES["effects"]: "".join(effects), DRAKE_FILES["triggers"]: triggers, DRAKE_FILES["loc"]: loc_text,
            DRAKE_FILES["weapons"]: "".join(weapons)}


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
    out[SPECIALIST_AUTOMATION_FILE] = generate_specialist_automation(game, giga)
    out[NANITE_SECTIONS_FILE] = generate_nanite_sections(game, giga)
    out[NANITE_SECTIONS_LOC_FILE] = generate_nanite_sections_loc(game, giga)
    out[NANITE_ENTITIES_FILE] = generate_nanite_entities(game, giga)
    out.update(generate_drakes(game))
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
