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


def fake_tech(key):
    return f"""{key} = {{
\tarea = physics
\tlevels = -1
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
        (self.game / "common/districts/00_urban_districts.txt").write_text(FAKE_DISTRICTS)
        (self.game / "common/ascension_perks/00_ascension_paths.txt").write_text(FAKE_APS)
        (self.game / "common/situations/08_machine_age_situations.txt").write_text(FAKE_SITUATIONS)
        (self.game / "launcher-settings.json").write_text('{ "rawVersion": "v9.9.9" }')
        (self.game / "events").mkdir()
        (self.game / "events/machine_age_situation_events_3.txt").write_text(FAKE_EVENTS)
        self.giga = self.tmp / "giga"
        (self.giga / "descriptor.mod").parent.mkdir(parents=True)
        (self.giga / "descriptor.mod").write_text('version="8.8.8"\n')
        techs = {}
        for _suffix, tech, _area, src, _potential in gen_overrides.SHELVE:
            techs.setdefault(src, []).append(tech)
        for src, keys in techs.items():
            path = (self.giga / src[len(gen_overrides.GIGA):]) if src.startswith(gen_overrides.GIGA) else self.game / src
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(fake_tech(k) for k in keys))
        script = self.giga / gen_overrides.MEGA_CAP_SCRIPT
        script.parent.mkdir(parents=True)
        script.write_bytes(FAKE_MEGA_CAP_SCRIPT.encode())

    def generate(self):
        return gen_overrides.generate(self.game, self.giga)

    def test_inserts_snippets_and_keeps_vanilla_text(self):
        out = self.generate()
        aps = out["mod/common/ascension_perks/zz_lfg_ascension_path_overrides.txt"]
        self.assertIn("Stellaris v9.9.9", aps)
        self.assertNotIn("ap_other", aps)
        self.assertEqual(aps.count("has_valid_civic = civic_lfg_pampered_masters"), 2)
        # Removing the marked additions gives back the vanilla blocks exactly.
        stripped = aps.replace("\t\t# LFG: added by stellaris-lfg-traditions\n" + gen_overrides.FLESH_BLOCK, "")
        self.assertIn(gen_overrides.extract_block(FAKE_APS, "ap_the_flesh_is_weak"), stripped)
        self.assertIn(gen_overrides.extract_block(FAKE_APS, "ap_synthetic_evolution"), stripped)
        sit = out["mod/common/situations/zz_lfg_situation_overrides.txt"]
        self.assertIn("\t\tbase = 15\n\t\t# LFG: added", sit)
        self.assertIn("add = value:lfg_synthetic_fertility_acceleration", sit)

    def test_resort_district_gets_extra_jobs_block(self):
        out = self.generate()
        districts = out["mod/common/districts/zz_lfg_district_overrides.txt"]
        self.assertNotIn("district_city", districts)
        self.assertIn("\t# LFG: added by stellaris-lfg-traditions\n\ttriggered_planet_modifier = {", districts)
        self.assertIn("has_active_tradition = tr_lfg_resorts_hospitality_academies", districts)
        self.assertIn("planet_max_districts_add = @lfg_resort_districts_per_district", districts)
        # the vanilla block comes first, unchanged
        self.assertLess(districts.index("job_resort_worker_add = @special_district_jobs"),
                        districts.index("job_resort_worker_add = @lfg_resort_extra_district_jobs"))

    def test_holomuseums_get_holo_museums_block(self):
        out = self.generate()["mod/common/buildings/zz_lfg_building_overrides.txt"]
        self.assertEqual(out.count("has_active_tradition = tr_lfg_broadcast_holo_museums"), 3)
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
        (self.game / "common/ascension_perks/00_ascension_paths.txt").write_text("ap_other = { }\n")
        with self.assertRaisesRegex(gen_overrides.GenError, "ap_the_flesh_is_weak"):
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
