"""check_mod.py tests: the real mod must pass, and each kind of mistake (applied to a copy) must be caught."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import check_mod  # noqa: E402

GAME_INSTALLED = check_mod.DEFAULT_GAME.exists() and check_mod.DEFAULT_GIGA.exists()
TRADITIONS = "common/traditions/lfg_traditions.txt"
CATEGORIES = "common/tradition_categories/lfg_tradition_categories.txt"
CIVICS = "common/governments/civics/lfg_civics.txt"
TRAD_LOC = "localisation/english/lfg_traditions_l_english.yml"
GFX = "interface/lfg_traditions.gfx"
EVENTS = "events/lfg_species_split_events.txt"
EDICTS = "common/edicts/lfg_edicts.txt"
SPLIT_EFFECTS = "common/scripted_effects/lfg_species_split_effects.txt"
CIVIC_LOC = "localisation/english/lfg_civics_l_english.yml"
AGENDA_LOC = "localisation/english/lfg_agendas_l_english.yml"
STATICS = "common/static_modifiers/lfg_static_modifiers.txt"
POLYMATH_EVENTS = "events/lfg_polymath_events.txt"
ON_ACTIONS = "common/on_actions/lfg_on_actions.txt"
POLICY_LOC = "localisation/english/lfg_policies_l_english.yml"


def failures(mod_dir, game=None, giga=None):
    return check_mod.run(mod_dir, game, giga, modifiers_log=None).failures


class RealModTests(unittest.TestCase):
    def test_passes_without_game_files(self):
        self.assertEqual(failures(REPO / "mod"), [])

    @unittest.skipUnless(GAME_INSTALLED, "Stellaris + Gigastructural not installed")
    def test_passes_with_game_files(self):
        r = check_mod.run(REPO / "mod", check_mod.DEFAULT_GAME, check_mod.DEFAULT_GIGA,
                          check_mod.DEFAULT_MODIFIERS_LOG, require_sources=True)
        self.assertEqual(r.failures, [])

    def test_mod_contents(self):
        mod = check_mod.Mod(REPO / "mod", check_mod.Report(False))
        self.assertEqual(len(mod.top("common/tradition_categories")), 9)
        self.assertEqual(len(mod.top("common/traditions")), 9 * 7)
        self.assertIn("civic_lfg_pampered_masters", mod.top("common/governments/civics"))
        self.assertIn("lfg_species_experimentation", mod.top("common/edicts"))
        self.assertEqual(check_mod.mod_event_ids(mod), {"lfg_species_split.1", "lfg_polymath.1", "lfg_polymath.2", "lfg_polymath.3"})
        self.assertEqual(len(mod.top("common/council_agendas")), 9)


class MutationTests(unittest.TestCase):
    """Copy mod/, break one thing, expect a specific failure."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.mod = self.tmp / "mod"
        shutil.copytree(REPO / "mod", self.mod)

    def edit(self, rel, old, new, count=1):
        path = self.mod / rel
        data = path.read_bytes()
        self.assertIn(old.encode(), data, f"fixture text not found in {rel}: {old!r}")
        path.write_bytes(data.replace(old.encode(), new.encode(), count))

    def assertFails(self, needle, **kw):
        found = failures(self.mod, **kw)
        self.assertTrue(any(needle in f for f in found), f"expected a failure containing {needle!r}, got {found}")

    def test_unknown_modifier(self):
        self.edit(TRADITIONS, "megastructure_build_speed_mult = 0.10", "megastructure_build_cost_mult = 0.10")
        self.assertFails("unknown modifier megastructure_build_cost_mult")

    def test_non_numeric_modifier(self):
        self.edit(TRADITIONS, "pop_happiness = 0.05", "pop_happiness = yes")
        self.assertFails("non-numeric value")

    def test_parse_error(self):
        self.edit(CIVICS, "modification = no", "modification = no {")
        self.assertFails("parse error")

    def test_missing_tradition_definition(self):
        self.edit(CATEGORIES, '"tr_lfg_leisure_arts"', '"tr_lfg_leisure_artz"')
        self.assertFails("tr_lfg_leisure_artz is not defined")

    def test_tradition_not_in_any_tree(self):
        self.edit(CATEGORIES, '\t\t"tr_lfg_leisure_arts"\n', "")
        self.assertFails("tr_lfg_leisure_arts: defined but not part of any tradition category")
        self.assertFails("expected 5 traditions, found 4")

    def test_prerequisite_outside_tree(self):
        self.edit(TRADITIONS, "has_tradition = tr_lfg_megaforge_priority", "has_tradition = tr_lfg_leisure_arts")
        self.assertFails("requires tr_lfg_leisure_arts, which is not in tradition_lfg_megaforge")

    def test_prerequisite_wrong_shape(self):
        self.edit(TRADITIONS, "\t\thas_tradition = tr_lfg_leisure_markets\n", "")
        self.assertFails("should require slots [1, 2]")

    def test_unknown_tree_template(self):
        self.edit(CATEGORIES, 'tree_template = "tree_21_11"', 'tree_template = "tree_99"')
        self.assertFails("unknown tree_template")

    def test_missing_loc_key(self):
        self.edit(TRAD_LOC, " tr_lfg_leisure_arts_delayed:", " tr_lfg_leisure_artsXX_delayed:")
        self.assertFails("missing localisation: tr_lfg_leisure_arts_delayed")

    def test_duplicate_loc_key(self):
        self.edit(TRAD_LOC, " tr_lfg_leisure_arts_delayed:", " tr_lfg_leisure_arts_desc:")
        self.assertFails("duplicate localisation key tr_lfg_leisure_arts_desc")

    def test_loc_without_bom(self):
        path = self.mod / TRAD_LOC
        path.write_bytes(path.read_bytes()[3:])
        self.assertFails("missing UTF-8 BOM")

    def test_malformed_loc_line(self):
        self.edit(TRAD_LOC, ' tradition_lfg_leisure:0 "Leisure Society"', ' tradition_lfg_leisure:0 Leisure Society')
        self.assertFails("malformed localisation line")

    def test_unbalanced_colour_code(self):
        self.edit(TRAD_LOC, "§YMega-Engineering§!", "§YMega-Engineering")
        self.assertFails("unbalanced § colour codes")

    def test_loc_reference_without_loc(self):
        self.edit(CIVICS, "description = civic_tooltip_lfg_pampered_masters_effects",
                  "description = civic_tooltip_lfg_pampered_masters_effectz")
        self.assertFails("has no localisation")

    def test_missing_sprite(self):
        self.edit(GFX, 'name = "GFX_tr_lfg_leisure_arts"', 'name = "GFX_tr_lfg_leisure_artz"')
        self.assertFails("missing sprite GFX_tr_lfg_leisure_arts")

    def test_missing_category_sprite(self):
        self.edit(GFX, 'name = "GFX_tradition_hex_bg_tradition_lfg_overclock"', 'name = "GFX_x"')
        self.assertFails("missing sprite GFX_tradition_hex_bg_tradition_lfg_overclock")

    def test_unprefixed_key(self):
        self.edit(CIVICS, "civic_lfg_pampered_masters = {", "civic_pampered_masters = {")
        self.assertFails("lacks an lfg prefix")

    def test_unexpected_file(self):
        (self.mod / "common/events_by_mistake.txt").write_text("x = 1\n")
        self.assertFails("unexpected file in mod/")

    def test_override_file_outside_generator(self):
        (self.mod / "common/ascension_perks/my_ap.txt").write_text("ap_x = { }\n")
        self.assertFails("unexpected file in mod/")

    def test_descriptor_path(self):
        with open(self.mod / "descriptor.mod", "a") as f:
            f.write('path="/tmp/x"\n')
        self.assertFails("must not contain path=")

    def test_thumbnail_not_png(self):
        (self.mod / "thumbnail.png").write_text("nope")
        self.assertFails("thumbnail.png is not a PNG")

    def test_override_references_missing_script_value(self):
        self.edit("common/script_values/lfg_script_values.txt", "lfg_synthetic_fertility_acceleration = {",
                  "lfg_renamed = {")
        self.assertFails("value:lfg_synthetic_fertility_acceleration is not defined")

    def test_fired_event_must_exist(self):
        self.edit(EDICTS, "country_event = { id = lfg_species_split.1 }", "country_event = { id = lfg_species_split.2 }")
        self.assertFails("fires lfg_species_split.2, which is not defined")

    def test_event_loc_missing(self):
        self.edit(CIVIC_LOC, " lfg_species_split.1.others:", " lfg_species_split.1.otherz:")
        self.assertFails("uses lfg_species_split.1.others, which has no localisation")

    def test_event_id_outside_namespace(self):
        self.edit(EVENTS, "id = lfg_species_split.1\n", "id = lfg_other.1\n")
        self.assertFails("not in this file's namespace")

    def test_event_namespace_prefix(self):
        self.edit(EVENTS, "namespace = lfg_species_split", "namespace = species_split")
        self.assertFails("namespace species_split lacks an lfg prefix")

    def test_edict_loc_missing(self):
        self.edit(CIVIC_LOC, " edict_lfg_species_experimentation_desc:", " edict_lfg_species_experimentation_dezc:")
        self.assertFails("missing localisation: edict_lfg_species_experimentation_desc")

    def test_undefined_scripted_trigger(self):
        self.edit(EDICTS, "lfg_species_split_eligible = yes", "lfg_species_split_eligable = yes")
        self.assertFails("lfg_species_split_eligable is not a scripted trigger/effect")

    def test_undefined_script_value(self):
        self.edit(SPLIT_EFFECTS, "value:lfg_species_split_share", "value:lfg_species_split_shar")
        self.assertFails("value:lfg_species_split_shar is not defined")

    @unittest.skipUnless(GAME_INSTALLED, "Stellaris + Gigastructural not installed")
    def test_undefined_mod_variable(self):
        self.edit(SPLIT_EFFECTS, "count = @lfg_species_split_count", "count = @lfg_species_split_cnt")
        self.assertFails("scripted variable @lfg_species_split_cnt is not defined",
                         game=check_mod.DEFAULT_GAME, giga=check_mod.DEFAULT_GIGA)

    def test_agenda_loc_missing(self):
        self.edit(AGENDA_LOC, " council_agenda_agenda_lfg_eureka_season_desc:", " council_agenda_agenda_lfg_eureka_season_dezc:")
        self.assertFails("missing localisation: council_agenda_agenda_lfg_eureka_season_desc")

    def test_unknown_agenda(self):
        self.edit(TRADITIONS, "unlocks_agenda = agenda_lfg_eureka_season", "unlocks_agenda = agenda_lfg_eureka_seasonn")
        self.assertFails("unlocks_agenda agenda_lfg_eureka_seasonn is not defined")

    def test_agenda_finish_modifier_missing(self):
        self.edit(STATICS, "agenda_lfg_gala_season_finish = {", "agenda_lfg_gala_seasons_finish = {")
        self.assertFails("finish_modifier agenda_lfg_gala_season_finish is not defined")

    def test_static_modifier_unknown_modifier(self):
        self.edit(STATICS, "planet_researchers_produces_mult = -0.25", "planet_researcher_produces_mult = -0.25")
        self.assertFails("static modifier lfg_lab_accident: unknown modifier planet_researcher_produces_mult")

    def test_add_modifier_undefined(self):
        self.edit(POLYMATH_EVENTS, "modifier = lfg_lab_accident ", "modifier = lfg_lab_accidents ")
        self.assertFails("add_modifier lfg_lab_accidents is not defined")

    def test_on_action_event_missing(self):
        self.edit(ON_ACTIONS, "lfg_polymath.1", "lfg_polymath.9")
        self.assertFails("on_yearly_pulse_country fires lfg_polymath.9, which is not defined")

    def test_policy_flag_not_set(self):
        self.edit(TRADITIONS, "potential = { has_policy_flag = lfg_people_first }", "potential = { has_policy_flag = lfg_peoples_first }")
        self.assertFails("has_policy_flag = lfg_peoples_first is not set by any policy option")

    def test_policy_bad_category(self):
        self.edit("common/policies/lfg_policies.txt", "category = economy", "category = economic")
        self.assertFails("policy category must be one of")

    def test_policy_option_loc_missing(self):
        self.edit(POLICY_LOC, " lfg_monument_economy_people_first_desc:", " lfg_monument_economy_people_first_dezc:")
        self.assertFails("missing localisation: lfg_monument_economy_people_first_desc")

    def test_decision_loc_missing(self):
        self.edit("localisation/english/lfg_decisions_l_english.yml", " decision_lfg_expand_resort_desc:", " decision_lfg_expand_resort_dezc:")
        self.assertFails("missing localisation: decision_lfg_expand_resort_desc")

    @unittest.skipUnless(GAME_INSTALLED, "Stellaris + Gigastructural not installed")
    def test_generated_modifier_without_loc(self):
        self.edit("localisation/english/lfg_modifiers_l_english.yml", " mod_pop_resort_worker_bonus_workforce_mult:", " mod_pop_resort_workerz_bonus_workforce_mult:")
        self.assertFails("modifier pop_resort_worker_bonus_workforce_mult has no localisation",
                         game=check_mod.DEFAULT_GAME, giga=check_mod.DEFAULT_GIGA)

    @unittest.skipUnless(GAME_INSTALLED, "Stellaris + Gigastructural not installed")
    def test_hidden_modifiers_need_no_loc(self):
        # Grand Works Priority's 44 district lines are in a static modifier behind show_only_custom_tooltip.
        found = failures(self.mod, game=check_mod.DEFAULT_GAME, giga=check_mod.DEFAULT_GIGA)
        self.assertFalse(any("planet_district_arcology_housing_build_speed_mult" in f for f in found), found)

    def test_show_only_custom_tooltip_in_tradition_is_rejected(self):
        self.edit(TRADITIONS, "\t\tmegastructure_build_speed_mult = 0.20\n\t\tplanet_structures_cost_mult = 0.30",
                  "\t\tshow_only_custom_tooltip = yes\n\t\tmegastructure_build_speed_mult = 0.20\n\t\tplanet_structures_cost_mult = 0.30")
        self.assertFails("tr_lfg_megaforge_priority: show_only_custom_tooltip has no effect here")

    def test_require_sources_turns_skips_into_failures(self):
        r = check_mod.run(self.mod, None, None, None, require_sources=True)
        self.assertTrue(any("--require-sources" in f for f in r.failures))

    @unittest.skipUnless(GAME_INSTALLED, "Stellaris + Gigastructural not installed")
    def test_unknown_technology(self):
        self.edit(TRADITIONS, "has_technology = tech_robotic_workers", "has_technology = tech_robotic_workerz")
        self.assertFails("tech_robotic_workerz is not defined",
                         game=check_mod.DEFAULT_GAME, giga=check_mod.DEFAULT_GIGA)

    @unittest.skipUnless(GAME_INSTALLED, "Stellaris + Gigastructural not installed")
    def test_unknown_building(self):
        self.edit(TRADITIONS, "has_building = galactic_history_holomuseum", "has_building = galactic_history_museum")
        self.assertFails("has_building = galactic_history_museum is not defined",
                         game=check_mod.DEFAULT_GAME, giga=check_mod.DEFAULT_GIGA)

    @unittest.skipUnless(GAME_INSTALLED, "Stellaris + Gigastructural not installed")
    def test_unknown_origin_in_civic(self):
        self.edit(CIVICS, "value = origin_mechanists", "value = origin_mechanistz")
        self.assertFails("origin value origin_mechanistz is not defined",
                         game=check_mod.DEFAULT_GAME, giga=check_mod.DEFAULT_GIGA)

    @unittest.skipUnless(GAME_INSTALLED, "Stellaris + Gigastructural not installed")
    def test_missing_texture(self):
        self.edit(GFX, "tradition_icon_harmony.dds", "tradition_icon_harmonyz.dds")
        self.assertFails("texture not found", game=check_mod.DEFAULT_GAME, giga=check_mod.DEFAULT_GIGA)

    @unittest.skipUnless(GAME_INSTALLED, "Stellaris + Gigastructural not installed")
    def test_hand_edited_override(self):
        self.edit("common/situations/zz_lfg_situation_overrides.txt", "initial_progress = 300", "initial_progress = 0")
        self.assertFails("is stale", game=check_mod.DEFAULT_GAME, giga=check_mod.DEFAULT_GIGA)


if __name__ == "__main__":
    unittest.main()
