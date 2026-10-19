"""gen_overrides.py tests against a tiny fake game directory."""
import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import gen_overrides  # noqa: E402

FAKE_APS = """\
ap_other = {
\tpossible = { always = yes }
}

ap_the_flesh_is_weak = {
\ton_enabled = { custom_tooltip = "flesh_is_weak_tooltip" } # a { brace in a comment
\tpossible = {
\t\tcustom_tooltip = { fail_text = "x" always = yes }
\t}
\tpotential = { is_gestalt = no }
}

ap_synthetic_evolution = {
\tpossible = {
\t\talways = yes
\t}
}
"""

FAKE_SITUATIONS = """\
situation_synthetic_fertility_digitization = {
\ton_monthly = {
\t\tevents = {
\t\t\tmachine_age.3325 #Monthly Progress
\t\t}
\t}
\tinitial_progress = 300
\tmonthly_progress = {
\t\tbase = 15
\t}
}
"""


FAKE_DISTRICTS = """\
district_city = {
\tbase_buildtime = 480
}

district_resort = {
\tbase_buildtime = 480
\ttriggered_planet_modifier = {
\t\tpotential = {
\t\t\texists = owner
\t\t\towner = {
\t\t\t\tis_regular_empire = yes
\t\t\t}
\t\t}
\t\tmodifier = {
\t\t\tjob_resort_worker_add = @special_district_jobs
\t\t}
\t}
}
"""


def fake_holomuseum(key, research):
    return f"""{key} = {{
\tbase_buildtime = 360
\ttriggered_planet_modifier = {{
\t\tpotential = {{
\t\t\texists = owner
\t\t\towner = {{
\t\t\t\tis_regular_empire = yes
\t\t\t}}
\t\t}}
\t\tplanet_entertainers_unity_produces_add = 0.25
\t\tplanet_entertainers_{research}_research_produces_add = 0.25
\t\tplanet_entertainers_consumer_goods_upkeep_add = 0.25
\t}}
}}
"""


FAKE_RESEARCH_BUILDINGS = (
    "building_archaeostudies_faculty = {\n\tbase_buildtime = 360\n\n\tplanet_modifier = {\n"
    "\t\tplanet_biologists_society_research_produces_add = 0.25\n\t}\n}\n")

FAKE_BUILDINGS = "".join(fake_holomuseum(k, r) for k, r in (
    ("xeno_geology_holomuseum", "engineering"), ("aesthetic_wonders_holomuseum", "physics"),
    ("galactic_history_holomuseum", "society")))


FAKE_EVENTS = """\
namespace = machine_age

situation_event = { # Tradition 0
\tid = machine_age.4390
\toption = {
\t\tname = "machine_age.4400.c"
\t}
}

situation_event = { # Tradition 1
\tid = machine_age.4400
\toption = {
\t\tname = "machine_age.4400.a"
\t}
\toption = {
\t\tname = "machine_age.4400.c"
\t\towner = { set_country_flag = transformation_virtuality }
\t}
}
"""


def fake_zone(key):
    return f"""{key} = {{
\tbase_buildtime = @zone_buildtime
\tzone_sets = {{
\t\tresort
\t}}
\tmax_buildings = 1
}}
"""


FAKE_ZONES = "zone_urban = {\n\tzone_sets = {\n\t\turban\n\t}\n}\n" + "".join(
    fake_zone(z) for z, _job, _amount in gen_overrides.RESORT_ZONES) + "".join(
    fake_zone(z) for z, _jobs in gen_overrides.PENAL_ZONES)


def fake_tech(key, evidence=None):
    modifier = f"\tmodifier = {{ {evidence} }}\n" if evidence else ""
    return f"""{key} = {{
\tarea = physics
{modifier}\tlevels = -1
#\tweight_modifier = {{ commented out }}
\tweight_modifier = {{
\t\tfactor = @repatableTechFactor
\t}}
}}
"""


# Giga's inline script: 4-space indentation, commented header line, CRLF, no trailing newline.
FAKE_MEGA_CAP_SCRIPT = (
    "#giga_tech_repeatable_$name$_cap = {\r\n    area = $area$\r\n    tier = 5\r\n"
    "    weight_modifier = {\r\n        modifier = {\r\n            factor = 0\r\n        }\r\n    }\r\n#}"
)


class GenOverridesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.game = self.tmp / "game"
        (self.game / "common/ascension_perks").mkdir(parents=True)
        (self.game / "common/situations").mkdir(parents=True)
        (self.game / "common/districts").mkdir(parents=True)
        (self.game / "common/buildings").mkdir(parents=True)
        (self.game / "common/buildings/21_grand_archive_buildings.txt").write_text(FAKE_BUILDINGS)
        (self.game / "common/buildings/05_research_buildings.txt").write_text(FAKE_RESEARCH_BUILDINGS)
        (self.game / "common/districts/00_urban_districts.txt").write_text(FAKE_DISTRICTS)
        (self.game / "common/ascension_perks/00_ascension_paths.txt").write_text(FAKE_APS)
        (self.game / "common/situations/08_machine_age_situations.txt").write_text(FAKE_SITUATIONS)
        (self.game / "launcher-settings.json").write_text('{ "rawVersion": "v9.9.9" }')
        (self.game / "events").mkdir()
        (self.game / "common/planet_classes").mkdir()
        (self.game / "common/planet_classes/00_planet_classes.txt").write_text(
            "pc_desert = {\n\tcolonizable = yes\n}\npc_barren = {\n\tcolonizable = no\n}\npc_ocean = {\n\tcolonizable = yes\n}\n")
        (self.tmp / "giga/common/planet_classes").mkdir(parents=True)
        (self.tmp / "giga/common/planet_classes/giga_planet_classes.txt").write_text("pc_flat_world = {\r\n\tcolonizable = yes\r\n}\r\n")
        (self.game / "common/zones").mkdir()
        (self.game / "common/zones/00_zones.txt").write_text(FAKE_ZONES)
        (self.game / "events/machine_age_situation_events_3.txt").write_text(FAKE_EVENTS)
        self.giga = self.tmp / "giga"
        (self.giga / "descriptor.mod").parent.mkdir(parents=True, exist_ok=True)
        (self.giga / "descriptor.mod").write_text('version="8.8.8"\n')
        techs = {}
        for suffix, tech, _area, src, _potential in gen_overrides.SHELVE:
            techs.setdefault(src, []).append((tech, gen_overrides.SHELVE_EFFECTS[suffix][1]))
        for src, keys in techs.items():
            path = (self.giga / src[len(gen_overrides.GIGA):]) if src.startswith(gen_overrides.GIGA) else self.game / src
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(fake_tech(k, ev) for k, ev in keys))
        (self.giga / "localisation/english").mkdir(parents=True)
        (self.giga / "localisation/english/giga_l_english.yml").write_text(
            '\ufeffl_english:\r\n  origin_great_ring_desc:0 "Lore."\r\n  origin_tooltip_great_ring_effects:0 "Start on a ring.\\n- Hab."\r\n',
            encoding="utf-8")
        (self.giga / "localisation/english/giga_alderson_l_english.yml").write_text(
            '\ufeffl_english:\n  origin_alderson_effects:0 "Start on a slice."\n', encoding="utf-8")
        script = self.giga / gen_overrides.MEGA_CAP_SCRIPT
        script.parent.mkdir(parents=True)
        script.write_bytes(FAKE_MEGA_CAP_SCRIPT.encode())

    def generate(self):
        return gen_overrides.generate(self.game, self.giga)

    def test_inserts_snippets_and_keeps_vanilla_text(self):
        out = self.generate()
        sit = out["mod/common/situations/zz_lfg_situation_overrides.txt"]
        self.assertIn("Stellaris v9.9.9", sit)
        # One copy of the situation with both insertions; removing them gives back the vanilla block exactly.
        self.assertEqual(sit.count("situation_synthetic_fertility_digitization = {"), 1)
        self.assertIn("\t\t\tmachine_age.3325 #Monthly Progress\n\t\t\t# LFG: added by stellaris-lfg-traditions\n"
                      "\t\t\tlfg_synthetic_fertility.1", sit)
        stripped = sit.replace("\t\t# LFG: added by stellaris-lfg-traditions\n" + gen_overrides.SYNTH_FERTILITY_BLOCK, "")
        stripped = stripped.replace("\t\t\t# LFG: added by stellaris-lfg-traditions\n" + gen_overrides.SYNTH_FERTILITY_UPLOAD, "")
        self.assertIn(FAKE_SITUATIONS, stripped)
        self.assertIn("\t\tbase = 15\n\t\t# LFG: added", sit)
        self.assertIn("add = value:lfg_synthetic_fertility_acceleration", sit)

    def test_resort_district_gets_extra_jobs_block(self):
        out = self.generate()
        districts = out["mod/common/districts/zz_lfg_district_overrides.txt"]
        self.assertNotIn("district_city", districts)
        self.assertIn("\t# LFG: added by stellaris-lfg-traditions\n\ttriggered_planet_modifier = {", districts)
        self.assertIn("has_active_tradition = tr_lfg_tourism_hospitality_academies", districts)
        self.assertIn("planet_max_districts_add = @lfg_resort_districts_per_district", districts)
        # the vanilla block comes first, unchanged
        self.assertLess(districts.index("job_resort_worker_add = @special_district_jobs"),
                        districts.index("job_resort_worker_add = @lfg_resort_extra_district_jobs"))

    def test_archaeostudies_faculty_gets_expedition_corps_block(self):
        out = self.generate()["mod/common/buildings/zz_lfg_building_overrides.txt"]
        block = gen_overrides.extract_block(out, "building_archaeostudies_faculty")
        self.assertIn("has_active_tradition = tr_lfg_xenoarchaeology_expedition_corps", block)
        self.assertIn("planet_biologists_produces_mult = 0.25", block)

    def test_holomuseums_get_holo_museums_block(self):
        out = self.generate()["mod/common/buildings/zz_lfg_building_overrides.txt"]
        # one planet block (entertainer research) and one country block (specimens) per holomuseum
        self.assertEqual(out.count("has_active_tradition = tr_lfg_broadcast_holo_museums"), 6)
        for specimens in ("xeno_geology", "aesthetic_wonder", "historical_item"):
            self.assertEqual(out.count(f"{specimens}_specimens_produces_mult = @holomuseum_specimen_produces_mult"), 1)
        for research in ("engineering", "physics", "society"):
            self.assertEqual(out.count(f"planet_entertainers_{research}_research_produces_add = 0.25"), 2)
        # upkeep is not doubled
        self.assertEqual(out.count("planet_entertainers_consumer_goods_upkeep_add"), 3)

    def test_every_shelved_repeatable_checks_its_edict(self):
        out = self.generate()
        techs = out["mod/common/technology/zz_lfg_repeatable_overrides.txt"]
        self.assertIn("Stellaris v9.9.9, Gigastructural 8.8.8", techs)
        for suffix, tech, _area, src, _potential in gen_overrides.SHELVE:
            block = gen_overrides.extract_block(techs, tech)
            self.assertIn("\tweight_modifier = {\n\t\t# LFG: added by stellaris-lfg-traditions\n\t\tmodifier = {\n"
                          f"\t\t\tfactor = 0\n\t\t\thas_edict = lfg_shelve_{suffix}\n\t\t}}\n"
                          "\t\tfactor = @repatableTechFactor\n", block)
        self.assertEqual(techs.count("has_edict"), len(gen_overrides.SHELVE))

    def test_megastructure_capacity_script_checks_area_edict(self):
        script = self.generate()["mod/" + gen_overrides.MEGA_CAP_SCRIPT]
        self.assertNotIn("\r", script)
        self.assertIn("#giga_tech_repeatable_$name$_cap = {\n", script)
        self.assertIn("    weight_modifier = {\n        # LFG: added by stellaris-lfg-traditions\n        modifier = {\n"
                      "            factor = 0\n            has_edict = lfg_shelve_megastructure_capacity_$area$\n"
                      "        }\n        modifier = {\n", script)
        self.assertTrue(script.endswith("#}\n"))

    def test_shelve_edicts_and_loc(self):
        out = self.generate()
        edicts = out[gen_overrides.SHELVE_EDICTS_FILE]
        loc = out[gen_overrides.SHELVE_LOC_FILE]
        self.assertTrue(loc.startswith("\ufeffl_english:\n"))
        for suffix, tech, area, _src, potential in gen_overrides.SHELVE:
            block = gen_overrides.extract_block(edicts, f"lfg_shelve_{suffix}")
            self.assertIn(f"\t\t\t{area}_research = @lfg_shelve_research_upkeep\n", block)
            self.assertIn(potential, block)
            self.assertIn(f' edict_lfg_shelve_{suffix}:0 "Shelve: ${tech}$"\n', loc)
        for area in gen_overrides.MEGA_CAP_AREAS:
            block = gen_overrides.extract_block(edicts, f"lfg_shelve_megastructure_capacity_{area}")
            self.assertIn(f"{area}_research = @lfg_shelve_research_upkeep", block)
            self.assertIn(f" edict_lfg_shelve_megastructure_capacity_{area}_desc:0", loc)
        self.assertEqual(edicts.count("has_ascension_perk = ap_lfg_curated_progress"), len(gen_overrides.SHELVE) + 3)

    def test_resort_zones_get_hospitality_jobs(self):
        out = self.generate()["mod/common/zones/zz_lfg_zone_overrides.txt"]
        self.assertNotIn("zone_urban", out)
        for zone, job, amount in gen_overrides.RESORT_ZONES:
            block = gen_overrides.extract_block(out, zone)
            self.assertIn("\t\tresort\n\t}\n\t# LFG: added by stellaris-lfg-traditions\n\ttriggered_district_planet_modifier = {", block)
            self.assertIn(f"\t\tjob_{job}_add = {amount}\n\t\tmult = 0.5\n", block)
            self.assertIn("has_active_tradition = tr_lfg_tourism_hospitality_academies", block)

    def test_origin_texts_mention_virtuality_block(self):
        loc = self.generate()[gen_overrides.LOC_OVERRIDES_FILE]
        self.assertTrue(loc.startswith("\ufeffl_english:\n"))
        self.assertIn(' origin_tooltip_great_ring_effects:0 "Start on a ring.\\n- Hab.\\n- §RIndividual machine', loc)
        self.assertIn(' origin_alderson_effects:0 "Start on a slice.\\n- §RIndividual machine', loc)
        self.assertNotIn("origin_great_ring_desc", loc)

    def test_missing_loc_key_fails(self):
        (self.giga / "localisation/english/giga_alderson_l_english.yml").write_text("\ufeffl_english:\n", encoding="utf-8")
        with self.assertRaisesRegex(gen_overrides.GenError, "origin_alderson_effects"):
            self.generate()

    def test_world_types_count_colonizable_classes(self):
        out = self.generate()[gen_overrides.WORLD_TYPES_FILE]
        for pc in ("pc_desert", "pc_ocean", "pc_flat_world"):
            self.assertIn(f"\tmodifier = {{ add = 1 any_owned_planet = {{ is_planet_class = {pc} }} }}\n", out)
        self.assertNotIn("pc_barren", out)

    def test_city_zones_get_prison_industry_jobs(self):
        out = self.generate()["mod/common/zones/zz_lfg_zone_overrides.txt"]
        for zone, jobs in gen_overrides.PENAL_ZONES:
            block = gen_overrides.extract_block(out, zone)
            self.assertIn("has_tradition = tr_lfg_penitence_prison_industry", block)
            self.assertIn("has_modifier = penal_colony", block)
            for job, amount in jobs:
                self.assertIn(f"\t\tjob_{job}_add = {amount}\n", block)
            self.assertIn("\t\tmult = 0.5\n\t}\n", block)

    def test_virtuality_option_blocked_for_ring_origins(self):
        out = self.generate()["mod/events/00_lfg_event_overrides.txt"]
        self.assertIn("\nnamespace = machine_age\n", out)
        self.assertNotIn("machine_age.4390", out)  # only the event with the right id
        self.assertIn('\t\tname = "machine_age.4400.c"\n\t\t# LFG: added by stellaris-lfg-traditions\n\t\tallow = {\n', out)
        self.assertIn("has_origin = origin_great_ring", out)
        self.assertIn("has_origin = origin_alderson", out)
        self.assertIn("is_individual_machine = yes", out)
        self.assertEqual(out.count("# LFG: added"), 1)

    def test_missing_event_fails(self):
        (self.game / "events/machine_age_situation_events_3.txt").write_text(FAKE_EVENTS.replace("4400", "4401"))
        with self.assertRaisesRegex(gen_overrides.GenError, "machine_age.4400"):
            self.generate()

    def test_shelve_descriptions_say_what_the_tech_does(self):
        loc = self.generate()[gen_overrides.SHELVE_LOC_FILE]
        self.assertIn("Each level gives: §G+5%§! mineral output from jobs.", loc)
        self.assertEqual(loc.count("Each level gives:"), len(gen_overrides.SHELVE) + len(gen_overrides.MEGA_CAP_AREAS))

    def test_changed_tech_value_fails(self):
        path = self.game / "common/technology/00_eng_tech_repeatable.txt"
        path.write_text(path.read_text().replace("planet_jobs_minerals_produces_mult = 0.05",
                                                 "planet_jobs_minerals_produces_mult = 0.10"))
        with self.assertRaisesRegex(gen_overrides.GenError, "update its SHELVE_EFFECTS"):
            self.generate()

    def test_extract_block_ignores_braces_in_comments_and_strings(self):
        block = gen_overrides.extract_block(FAKE_APS, "ap_the_flesh_is_weak")
        self.assertTrue(block.startswith("ap_the_flesh_is_weak = {"))
        self.assertTrue(block.endswith("}\n"))
        self.assertNotIn("ap_synthetic_evolution", block)

    def test_missing_anchor_fails(self):
        (self.game / "common/situations/08_machine_age_situations.txt").write_text(
            FAKE_SITUATIONS.replace("base = 15", "base = 20"))
        with self.assertRaisesRegex(gen_overrides.GenError, "anchor"):
            self.generate()

    def test_missing_definition_fails(self):
        (self.game / "common/situations/08_machine_age_situations.txt").write_text("situation_other = { }\n")
        with self.assertRaisesRegex(gen_overrides.GenError, "situation_synthetic_fertility_digitization"):
            self.generate()

    def test_check_mode_detects_stale_files(self):
        repo = self.tmp / "repo"
        args = ["--game", str(self.game), "--giga", str(self.giga), "--repo", str(repo)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gen_overrides.main(args + ["--check"]), 1)   # nothing generated yet
            self.assertEqual(gen_overrides.main(args), 0)
            self.assertEqual(gen_overrides.main(args + ["--check"]), 0)
            path = repo / "mod/common/situations/zz_lfg_situation_overrides.txt"
            path.write_text(path.read_text().replace("base = 15", "base = 16"))
            self.assertEqual(gen_overrides.main(args + ["--check"]), 1)


if __name__ == "__main__":
    unittest.main()
