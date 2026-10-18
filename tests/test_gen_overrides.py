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

    def test_inserts_snippets_and_keeps_vanilla_text(self):
        out = gen_overrides.generate(self.game)
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
        out = gen_overrides.generate(self.game)
        districts = out["mod/common/districts/zz_lfg_district_overrides.txt"]
        self.assertNotIn("district_city", districts)
        self.assertIn("\t# LFG: added by stellaris-lfg-traditions\n\ttriggered_planet_modifier = {", districts)
        self.assertIn("has_active_tradition = tr_lfg_resorts_hospitality_academies", districts)
        self.assertIn("planet_max_districts_add = @lfg_resort_districts_per_district", districts)
        # the vanilla block comes first, unchanged
        self.assertLess(districts.index("job_resort_worker_add = @special_district_jobs"),
                        districts.index("job_resort_worker_add = @lfg_resort_extra_district_jobs"))

    def test_holomuseums_get_holo_museums_block(self):
        out = gen_overrides.generate(self.game)["mod/common/buildings/zz_lfg_building_overrides.txt"]
        self.assertEqual(out.count("has_active_tradition = tr_lfg_broadcast_holo_museums"), 3)
        for research in ("engineering", "physics", "society"):
            self.assertEqual(out.count(f"planet_entertainers_{research}_research_produces_add = 0.25"), 2)
        # upkeep is not doubled
        self.assertEqual(out.count("planet_entertainers_consumer_goods_upkeep_add"), 3)

    def test_extract_block_ignores_braces_in_comments_and_strings(self):
        block = gen_overrides.extract_block(FAKE_APS, "ap_the_flesh_is_weak")
        self.assertTrue(block.startswith("ap_the_flesh_is_weak = {"))
        self.assertTrue(block.endswith("}\n"))
        self.assertNotIn("ap_synthetic_evolution", block)

    def test_missing_anchor_fails(self):
        (self.game / "common/situations/08_machine_age_situations.txt").write_text(
            FAKE_SITUATIONS.replace("base = 15", "base = 20"))
        with self.assertRaisesRegex(gen_overrides.GenError, "anchor"):
            gen_overrides.generate(self.game)

    def test_missing_definition_fails(self):
        (self.game / "common/ascension_perks/00_ascension_paths.txt").write_text("ap_other = { }\n")
        with self.assertRaisesRegex(gen_overrides.GenError, "ap_the_flesh_is_weak"):
            gen_overrides.generate(self.game)

    def test_check_mode_detects_stale_files(self):
        repo = self.tmp / "repo"
        args = ["--game", str(self.game), "--repo", str(repo)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gen_overrides.main(args + ["--check"]), 1)   # nothing generated yet
            self.assertEqual(gen_overrides.main(args), 0)
            self.assertEqual(gen_overrides.main(args + ["--check"]), 0)
            path = repo / "mod/common/situations/zz_lfg_situation_overrides.txt"
            path.write_text(path.read_text().replace("base = 15", "base = 16"))
            self.assertEqual(gen_overrides.main(args + ["--check"]), 1)


if __name__ == "__main__":
    unittest.main()
