# CLAUDE.md

Stellaris 4.5 gameplay mod (requires Gigastructural Engineering 4.5): 9 tradition trees, 7 council agenda definitions (6 agendas), the Evolutionary
Predators edict `lfg_species_experimentation`, the ascension perk
`ap_lfg_curated_progress` + 27 generated Shelve edicts, and generated overrides of 1 situation +
1 district (district_resort) + 8 resort zones + 12 city zones (Prison Industry) + 3 buildings (holomuseums) + 24 repeatable techs + Giga's megastructure-capacity inline script
+ event machine_age.4400 (Virtuality blocked for individual machines with Great Ring / Alderson Disk).
User-facing docs and the full effect tables are in README.md. **Keep README's tables in sync when you change numbers.**

## Commands

```sh
scripts/verify.sh                         # unittest (tests/) + tools/check_mod.py; run after every change
scripts/verify.sh --require-sources       # also fail if game/Giga files are missing (do before releases)
python3 -I tools/gen_overrides.py         # regenerate overrides + Shelve edicts/loc (after game/Giga updates or SHELVE edits)
python3 -I tools/check_mod.py --update-snapshot   # refresh tools/data/modifiers_4.5.txt.gz from modifiers.log
scripts/install.sh                        # install a "[LOCAL DEV]" copy (no remote_file_id) for in-game testing
RELEASE=1 scripts/install.sh              # exact copy; only for uploading via the Paradox launcher
DRY_RUN=1 scripts/publish.sh              # what a Workshop upload would send (no login)
STEAM_USER=<login> scripts/publish.sh "note"   # verify + upload with steamcmd (see Release)
```
Python 3.9+ stdlib only. Always run with `-I`.

## Layout

```
mod/                                  # exactly what ships
  common/tradition_categories/00_<tree name>_lfg.txt         # 8 trees, one per file (sort order, see below)
  common/traditions/lfg_traditions.txt                       # adopt/finish + 5 traditions per tree
  common/governments/civics/lfg_civics.txt                   # civic_lfg_applied_biosciences (Biologists: society -> some physics/engineering)
  common/megastructures/lfg_megastructures.txt               # Swarmforge (Nanite Armada perk): lfg_swarmforge_0 -> _ready (a shipyard)
  common/ship_sizes/lfg_ship_sizes.txt                       # lfg_nanite_war_moon / lfg_nanite_planetcraft (only built at a Swarmforge)
  common/section_templates/lfg_nanite_section_templates.txt  # GENERATED (NANITE_HULLS): Giga's moon / planetcraft sections for our hulls
  localisation/english/lfg_nanite_sections_l_english.yml     # GENERATED: their section names
  gfx/models/ships/lfg_nanite_celestials.asset               # GENERATED (NANITE_TEXTURES / _SKINS): nanite skins + grey goo swarm
  gfx/models/ships/lfg_mothership.asset                      # Mothership model (hand-written; its core world is generated above)
  gfx/models/ships/lfg_nanite_hulls.asset                    # moon escort rings, planetcraft look + hull frame (hand-written)
                                                             #   looks sit in a section (SECTION_BODIES) so the ship designer shows them
  common/scripted_triggers/zz_lfg_trigger_overrides.txt      # GENERATED: Giga's war moon / planet component triggers + our hulls
  common/component_templates/lfg_components.txt              # LFG_NANITE_SWARM_HANGAR, _RESHAPER (X) (Mothership only), _SIEGE_DRIVER (T; _MAGINOT twin: max 3 on a Maginot World),
                                                             #   _FLAK_SWARM (PD) (Mothership + Maginot World), _DISASSEMBLER (W), _STORM_AUTOCANNON (L, all nanite hulls), _ARMOR (any ship), LFG_SWARMER_/_INTERDICTOR_VAULT/_FOUNDRY (aux);
                                                             #   LFG_LM_ACCELERATOR_2, LFG_*_LM_ARMOR_6 (galvanic)
  common/scripted_effects/lfg_mothership_effects.txt         # lfg_mothership_grow_reserve / _deploy / _launch_reserve / _recall
  events/lfg_mothership_events.txt                           # .1/.2 monthly reserve; .3/.4 battle -> deploy; .5 recall when no enemy;
                                                             #   .6 one per empire (on_ship_built: delete + refund an extra); .7 Disassembler nanites + vanilla cracker
                                                             #   on_action (.8/.9 queued/unqueued)
  gfx/models/ships/lfg_megastructures.asset                  # Progenitor Forge (nanite rings + Giga's yards) and Swarmforge (nanite cage), around their stars
  interface/lfg_megastructures.gfx                           # megastructure build / outliner icons
  interface/lfg_components.gfx                               # component icons (gfx/interface/icons/ship_parts/lfg_*.dds: art/make_component_icons.py)
  common/component_sets/lfg_component_sets.txt               # their sets (name / icon)
  common/scripted_modifiers/lfg_scripted_modifiers.txt      # custom ship modifiers of the Mothership's swarm modules (read by lfg_mothership.2)
  common/technology/lfg_technology.txt                       # tech_lfg_swarmforge / _nanite_war_moon / _nanite_planetcraft (offered by the perk); _lm_accelerator_2 / _lm_armor_6 (galvanic civics)
  common/buildings/lfg_buildings.txt                         # building_lfg_nanite_automation + _nanite_consensus_1-4 (origin), _nanite_cognition_core, _nanotensile_converter (Nanotech)
  common/static_modifiers/lfg_specialist_automation.txt      # GENERATED (specialist_jobs in gen_overrides.py): Cognition Core job list
  common/deposits/lfg_deposits.txt                           # d_lfg_nanite_forge_star (+22 energy), Ancient harvester's huge / vast deposits
  common/starbase_buildings/zz_lfg_starbase_building_overrides.txt  # GENERATED: vanilla nanite_harvester, not beside ours
  common/starbase_buildings/lfg_starbase_buildings.txt       # lfg_broken_nanite_harvester -> lfg_ancient_nanite_harvester (Nanite Forge origin; never buildable)
  common/scripted_effects/lfg_nanite_forge_effects.txt       # lfg_forge_harvester_step (steps 1-14; 8+ only once restored), lfg_restore_forge_harvester, lfg_clear_forge_harvester
  events/lfg_nanite_forge_events.txt                         # .1 game start, .2 3-year cycle/repair, .3 repair on Nanotech, .4 removal
  common/governments/councilors/lfg_councilors.txt           # councilor_lfg_applied_biosciences (Chief Bioengineer, scientists)
  gfx/interface/icons/governments/civics/civic_lfg_*.dds     # civic icons, all one colour: art/make_civic_icons.py (new civic -> add to ICONS)
  common/script_values/lfg_script_values.txt                 # lfg_synthetic_fertility_acceleration, lfg_species_split_share
  common/scripted_variables/lfg_scripted_variables.txt       # @lfg_species_split_* tunables (50 / 100)
  common/scripted_triggers/lfg_species_split_triggers.txt    # lfg_species_split_eligible (species scope, prev = country)
  common/scripted_effects/lfg_species_split_effects.txt      # lfg_split_species (the split itself)
  common/edicts/lfg_edicts.txt                               # lfg_species_experimentation -> fires lfg_species_split.1
  events/lfg_species_split_events.txt                        # species picker event
  events/lfg_xenoarchaeology_events.txt                      # Xenoarchaeology: .1 anomaly count + minor artifacts (anomaly_success),
                                                             #   .2 Commission a Dig choice popup, .3 result
  common/artifact_actions/lfg_artifact_actions.txt           # artifact_lfg_commission_dig (Commissioned Digs) -> lfg_xenoarchaeology.2
  common/scripted_effects/lfg_xenoarchaeology_effects.txt    # lfg_commission_dig_site / _anomaly / _rift (refund if no spot)
  common/scripted_triggers/lfg_xenoarchaeology_triggers.txt  # lfg_can_commission_anomaly / _astral_rift, lfg_commission_anomaly_planet
  events/lfg_resorts_events.txt                              # Galactic Destination: resort world modifier + tourist count (monthly)
  events/lfg_shellworlders_events.txt                        # Shellworlders: lfg_shellworld_* modifiers on artificial worlds (monthly)
  common/scripted_effects/lfg_shellworlders_effects.txt      # lfg_sync_shellworld_modifier / _natural_world / lfg_sync_arc_neighbours
  events/lfg_synthetic_fertility_events.txt                  # lfg_synthetic_fertility.1: extra Identity Repository uploads (monthly)
  events/lfg_penal_events.txt                                # lfg_penal.1: Penitence penal colony modifiers + counts (monthly; only the penal colony + planets with our modifiers)
  events/lfg_stationcraft_events.txt                         # lfg_stationcraft.1: monthly colony / starbase / kilo / mega counts ->
  common/scripted_effects/lfg_stationcraft_effects.txt       #   lfg_stationcraft_sync: lfg_stationcraft_per_* country modifiers (multiplier = count)
  events/lfg_lineage_events.txt                              # lfg_lineage.1: Every Shore planet-type count (monthly cache)
  common/scripted_effects/lfg_penal_effects.txt              # lfg_sync_penal_modifier / lfg_sync_penal_unemployed / lfg_penal_ship_unemployed
  common/zones/lfg_zones.txt                                 # zone_lfg_penal_supertensiles, zone_lfg_penal_bulk_matter
  common/pop_jobs/lfg_jobs.txt                               # lfg_penal_supertensile_laborer, lfg_penal_matter_compactor
  common/economic_categories/lfg_economic_categories.txt     # planet_lfg_penal_laborers (the job's category)
  events/lfg_planet_events.txt                               # lfg_planet.1: strip per-planet modifiers on owner change
  events/lfg_lone_tide_events.txt                            # lfg_lone_tide.1 (global `event`, on_game_start): 75% spawn
  events/lfg_emberfall_events.txt                            # lfg_emberfall.1 (on_game_start): Emberfall, always, connected
  common/solar_system_initializers/lfg_system_initializers.txt # lfg_lone_tide_init, lfg_emberfall_init (usage_odds = 0)
  common/script_values/lfg_world_types_values.txt            # GENERATED lfg_count_world_types (colonizable planet classes; cached monthly by lfg_lineage.1)
  events/00_lfg_event_overrides.txt                          # GENERATED (machine_age.4400: Virtuality block); 00_ = loads first
  common/council_agendas/lfg_council_agendas.txt             # 7 agendas, unlocked by tree finishers
  common/static_modifiers/lfg_static_modifiers.txt           # agenda finish modifiers + per-planet tradition modifiers
  common/on_actions/lfg_on_actions.txt                       # monthly -> lfg_resorts.1 + lfg_shellworlders.1, anomaly_success -> lfg_xenoarchaeology.1,
                                                             #   colony transfer/ownerless -> lfg_planet.1
  common/decisions/lfg_decisions.txt                         # decision_lfg_expand_resort (Paradise Unbound), decision_lfg_expand_cell_blocks (Penitence finisher),
                                                             #   decision_lfg_nanite_pulse (Nanotech; from a star) -> events/lfg_nanite_pulse_events.txt, decision_lfg_mothership_crew (2,000 pops)
  common/traits/lfg_traits.txt                               # trait_lfg_inherited_genius (Evolutionary Predators only)
  common/traits/lfg_leader_traits.txt                        # leader_trait_lfg_massed_assault (given by events/lfg_massed_assault_events.txt)
  common/policies/lfg_policies.txt                           # lfg_monument_economy (unlocked by Monument Economy)
  common/ascension_perks/lfg_ascension_perks.txt             # ap_lfg_curated_progress (needs Gigastructural Constructs), ap_lfg_massed_assault
  common/edicts/lfg_shelve_edicts.txt                        # GENERATED Shelve edicts (from SHELVE in gen_overrides.py)
  common/technology/zz_lfg_repeatable_overrides.txt          # GENERATED (24 repeatables: factor 0 while shelved)
  common/inline_scripts/technology/giga_mega_repeatable.txt  # GENERATED whole-file override of Giga's inline script
  common/situations/zz_lfg_situation_overrides.txt           # GENERATED
  common/districts/zz_lfg_district_overrides.txt             # GENERATED (district_resort: Hospitality Academies jobs)
  common/buildings/zz_lfg_building_overrides.txt             # GENERATED (3 holomuseums: Holo-Museums bonus; Archaeostudies Faculty: Expedition Corps)
  common/zones/zz_lfg_zone_overrides.txt                     # GENERATED (8 resort zones: Hospitality Academies; 12 city zones:
                                                             #   Prison Industry; each +50% jobs on that colony type)
  interface/lfg_traditions.gfx                               # sprites -> vanilla/Giga .dds, plus the bulk matter zone icon
  gfx/interface/icons/districts/lfg_zone_penal_bulk_matter.dds # 64x64 zone icon (art/make_zone_icons.py, needs Pillow)
  gfx/interface/icons/*/lfg_*.dds, tradition_lfg_*, agenda_lfg_*  # our art (Pillow scripts in art/): make_component_icons (ship parts),
                                                             #   make_building_icons (Consensus, Nanotensile, Ancient harvester), make_megastructure_icons
                                                             #   (Swarmforge build + tech icon, Nanite Pulse), make_glyph_icons (Megaforge / Stationcraft
                                                             #   tradition + tree icons, agenda icons; our own drawings, no vanilla art)
  interface/lfg_council_agendas.gfx                          # GFX_council_agenda_icon_<agenda key>
  common/pop_jobs/zz_lfg_job_overrides.txt                   # GENERATED: replicator job +0.5 nanites upkeep for the Nanite Forge origin
  localisation/english/lfg_*_l_english.yml                   # UTF-8 BOM (lfg_modifiers_*: names for unnamed generated modifiers;
                                                             #   lfg_shelve_* is GENERATED)
tools/pdx.py          # small Paradox-script parser
tools/check_mod.py    # static verification (see README "Verification")
tools/gen_overrides.py
tools/data/modifiers_4.5.txt.gz       # modifier-name snapshot used when modifiers.log is absent (CI)
tests/                # unittest; mutation tests copy mod/, break one thing, expect a specific failure;
                      # test_publish.py dry-runs publish.sh (needs game + Giga, skipped in CI);
                      # test_install.py checks the [LOCAL DEV] / RELEASE=1 installs
workshop_description.txt   # Steam BBCode description (sent on every upload; SYNC_DESCRIPTION=0 to skip)
```

## Rules

- **Prefix everything** `lfg`: `tradition_lfg_*`, `tr_lfg_*`, `civic_lfg_*`, `lfg_*` (script values, loc). Other installed
  mods use `tr_est_*`, `tr_mt_*`, `tr_macroengineering_*`, `tr_gigaengineering_*`, `tr_gigabulwark_*`. Never redefine vanilla or Giga keys
  except through `tools/gen_overrides.py`. The checker enforces prefixes.
- **Never hand-edit generated files** (`zz_lfg_*`, `inline_scripts/technology/giga_mega_repeatable.txt`, `lfg_shelve_edicts.txt`,
  `lfg_shelve_l_english.yml`). Change `OVERRIDES` / `SHELVE` / the snippets in `tools/gen_overrides.py` and regenerate.
  Overrides are source text plus `# LFG: added` lines. `zz_` makes them load after vanilla (and `zz_lfg_` after Giga's `zz_giga_`).
  Sources prefixed `giga:` are read from the Giga dir; key `None` copies a whole file (inline scripts can't be overridden per block).
  Key `event:<id>` copies one event. **Events are first-definition-wins** (common/ is last-wins), so event overrides go in
  `events/00_lfg_event_overrides.txt` (sorts before vanilla's event files) with the vanilla `namespace` in `PRELUDE`;
  the checker exempts that file from the lfg event-namespace rules.
  Text of the game/Giga: `LOC_OVERRIDES` (source loc file, key, appended text) -> `localisation/english/replace/lfg_origin_overrides_l_english.yml`
  (the `replace/` folder wins over other mods' keys; the checker exempts those keys from the lfg-prefix rule).
- **Every modifier must exist in 4.5.** Look it up in
  `~/Documents/Paradox Interactive/Stellaris/logs/script_documentation/modifiers.log` (the checker does). Pitfalls:
  - `megastructures_cost_mult`, not `megastructure_build_cost_mult` (which doesn't exist)
  - no `planet_jobs_civilian_*`: use `planet_civilians_<res>_produces_add`, `pop_cat_civilian_*`, `job_civilian_*`
  - 4.x growth: `logistic_growth_mult` (organic), `planet_pop_assembly_mult` (robots); the old `pop_growth_*` names are gone
  - `planet_maintenance_drones_produces_mult` doesn't exist
  - Jobless pops of regular empires are **Civilians** (uncapped `civilian` job), not unemployed: `num_unemployed` is 0
    for them. Count `num_assigned_jobs = { job = civilian }` (verified: Idle Hands showed no bonus with num_unemployed).
  - Magnitudes: civilian `_produces_add` ~0.1–0.5, `planet_stability_add` 2–5, `planet_amenities_add` is in hundreds (100–500).
- **Supertensiles** = Giga resource `giga_sr_amb_megaconstruction`. It exists only when global flag `giga_buildcap_j` is set.
  Put supertensile modifiers in `triggered_modifier = { potential = { has_global_flag = giga_buildcap_j } ... }` with a
  `NOT = { has_global_flag = giga_buildcap_j }` fallback block. Giga turns flat `megastructure_build_speed_add` into supertensile
  income, so use `megastructure_build_speed_mult`.
- **Gating:** tree visibility is the category's `potential`; adoption requirements go in the `_adopt` tradition's `possible`.
  Useful triggers: `is_regular_empire`, `is_gestalt`, `is_machine_empire`, `is_individual_machine`, `is_synthetic_empire`,
  `has_cybernetic_ascension`, `has_synthetic_ascension`, `is_nomadic`, `has_origin`, `has_valid_civic`.
  Civic `potential`/`possible` use the list syntax `origin = { NOR = { value = ... } }` (see `common/governments/99_README_GOVERNMENT.txt`).
- **Civic `possible` can't see ascension perks.** Blocking a mid-game choice for some empires means overriding the thing
  that offers it (perk `possible`, or an event option's `allow`, like `machine_age.4400`) with a `custom_tooltip`/`fail_text`
  so it shows greyed out with a reason. (The mod has no civics now; Pampered Masters was removed.)
- **Loc** files must be UTF-8 **with BOM**, start with `l_english:`, one-space indent, `key:0 "text"`. Each tradition needs
  `key`, `key_desc`, `key_delayed`; each tree `tradition_lfg_x` + `_desc`; a civic `civic_x` + `_desc` + the `description`/
  `negative_description` keys. Balance every `§Y…§!` colour code.

## How the pieces connect (adding a tree)

1. `common/tradition_categories/00_<English tree name>_lfg.txt` (one tree per file; e.g. "Tourism" ->
   `00_grand_tour_lfg.txt`). The traditions window lists trees in load order = file name order, so this sorts the tree
   alphabetically among vanilla's `00_<tree>.txt` regular trees instead of after the `01_*` ascension trees (More
   Traditions does the same). The checker enforces the name. Then `tradition_lfg_<name> = { desc, potential, tree_template = "tree_21_11",
   adoption_bonus = "tr_lfg_<name>_adopt", finish_bonus = "tr_lfg_<name>_finish", traditions = { 5 keys in slot order }, ai_weight }`.
   Include the `@ap_pending_tradition_suppress` modifier, as vanilla does.
2. `common/traditions/lfg_traditions.txt`: `_adopt` (optional `possible`), `_finish` (`ascension_perks_add = 1`), 5 traditions.
   With `tree_21_11`, slot 4 needs `possible = { has_tradition = <slot1> has_tradition = <slot2> }` and slot 5 needs `<slot3>`.
   Penitence uses `tree_111_11` (two chains: 2 needs 1, 3 needs 2, 5 needs 4). No vanilla layout draws "three into one".
   Other layouts: see `interface/topbar_traditions_view.gui` in the game, and add their prerequisite shapes to `TEMPLATE_PREREQS` in `check_mod.py`.
3. `interface/lfg_traditions.gfx`: `GFX_tradition_hex_bg_<cat>`, `GFX_tradition_category_bg_<cat>`,
   `GFX_tradition_category_tile_<cat>` (`corneredTileSpriteType`, `borderSize = { x = 140 y = 140 }`),
   `GFX_tradition_category_icon_<cat>`, and `GFX_tr_lfg_<tradition>` for the 5 traditions. Point them at vanilla art under
   `gfx/interface/{traditions,tiles,icons/traditions}/`.
4. Loc keys (see Rules). Then the README table, then `scripts/verify.sh`. Update the tree count in
   `tests/test_check_mod.py::test_mod_contents`.

## Sources (macOS)

- Game: `~/Library/Application Support/Steam/steamapps/common/Stellaris` (version in `launcher-settings.json`, currently v4.5.2)
- Giga: `~/Library/Application Support/Steam/steamapps/workshop/content/281990/1121692237`
- Modifier list: `~/Documents/Paradox Interactive/Stellaris/logs/script_documentation/modifiers.log` (regenerated by the
  game's `script_docs` console command; it includes modifiers from the mods loaded at the time)
- Overridden definitions: see `OVERRIDES` in `tools/gen_overrides.py` (ascension paths, Synthetic Fertility situation,
  district_resort, holomuseums, the repeatable techs in `SHELVE`, Giga's `giga_mega_repeatable` inline script)

## Updating for a new Stellaris / Giga version

1. `scripts/verify.sh --require-sources`.
2. If overrides are stale, run `python3 -I tools/gen_overrides.py` and review `git diff mod/common/*/zz_lfg_*`. If an anchor
   no longer matches, update the anchor regex in `OVERRIDES`. Re-check that the change still makes sense, e.g. whether the
   situation's `base` is still 15.
3. In game, run `script_docs`, then `python3 -I tools/check_mod.py --update-snapshot`, then rerun verify. Fix any modifiers that were renamed.
4. Unknown tech/origin/civic errors mean the game or Giga renamed something. Find the new key in their `common/` files.
5. Bump `supported_version` and the Giga dependency name (it contains the Giga version, e.g. `(4.5)`) in `mod/descriptor.mod`,
   and `version`.

## Release

1. Bump `version` in `mod/descriptor.mod`, update README tables and `workshop_description.txt` if effects changed, and commit.
2. `scripts/verify.sh --require-sources`, then do an in-game smoke test via `scripts/install.sh`.
3. `STEAM_USER=<login> scripts/publish.sh "vX.Y.Z: what changed"`. It runs the tests and `check_mod.py --require-sources`,
   refuses a dirty `mod/`, stages `mod/` (minus `.DS_Store`), and uploads via steamcmd `workshop_build_item` (appid 281990).
   - First upload: creates a **private** item and appends `remote_file_id` to `mod/descriptor.mod`. Commit it, and set
     Gigastructural as a Required item on the Workshop page.
   - Make it public later with `VISIBILITY=0`.
4. steamcmd's VDF parser has **no escape sequences**: `"` inside a value ends it, even written as `\"`. `publish.sh`'s `vdf_value`
   converts double quotes to “typographic quotes”, and `tests/test_publish.py` checks the dry-run VDF quote count. Keep it that way.
5. **Steam's description limit is 8000 characters.** Over it, steamcmd uploads everything and then fails at "Committing
   update" with `Invalid Parameter`. publish.sh and `tests/test_workshop_description.py` check it; keep the page concise.
6. Never put Steam credentials in the repo or CI. `PUBLISH_SKIP_TESTS=1` exists only so `test_publish.py` doesn't recurse.

## Species Experimentation edict - how it works and what's unverified

- Edict `lfg_species_experimentation` (loc `edict_<key>`; potential: `has_origin = origin_evolutionary_predators` +
  `has_tradition = tr_mutation_finish`; allow: any owned species passes
  `lfg_species_split_eligible`) -> `effect` fires `lfg_species_split.1`.
- Why an edict and a popup: `button_effects` in the species screen run in **country** scope (the selected species isn't
  available), and the user chose an edict over overriding UIOD's species window. Picking happens in the event (4 random
  eligible candidates saved as `event_target:lfg_split_candidate_1..4`, "Show others" re-fires the event).
- `lfg_split_species` (country scope, needs `event_target:lfg_split_source`): `while` 50x: `modify_species` with
  `change_scoped_species = no` + `add_random_species_trait` (filter copied from vanilla `add_random_trait_evopred`), then a second `modify_species` on that variant for a random `organic negative` trait (leaves a pop-less intermediate species; opposites unfiltered), then
  for every owned pop group of the source species: `colony = { create_pop_group = { size = 0 species = variant
  effect = { transfer_pop_amount = { percentage = value:lfg_species_split_share } } } }` (pattern from vanilla
  `02_machine_age_effects.txt` cyberization). The share is 1/remaining (1/50 ... 1/1); `percentage` is a 0-1 fraction.
- "100 pops" = **raw population** (user's choice), not 100-pop units (`POP_BULK_UNIT_SIZE`). Never the main species or its
  subspecies (`NOR` of `is_exact_same_species` / `is_subspecies` / `is_same_species = prev.owner_species`). Half of every pop group of the species is killed (`kill_pop_group`
  `percentage = 0.5`) before the split.
- **Unverified in game** (verify first if it misbehaves): `prevprev` scoping in `lfg_species_split_eligible`; `percentage =
  value:...` accepting a script value; `root.lfg_split_remaining` resolving inside the script value; edict `length = 30`
  re-use; species name loc `[lfg_split_candidate_1.GetName]`.

## Tradition design: hooks and agendas

Flat percentage trees are boring and duplicate other tradition mods (More Traditions, Expanded Stellaris Traditions
already have Bureaucracy, Academy, Industry, Opulence, Nature...). Every tree here needs a **hook**: something that scales
with or depends on game state. Patterns used:
- **Scaling:** `triggered_modifier = { potential = { always = yes } <modifier> = <per-unit> mult = value:lfg_x }` with a capped
  script value in `common/script_values/lfg_script_values.txt` (`complex_trigger_modifier = { trigger = num_rivals mode = add }`,
  `trigger:years_passed`, stockpile via `trigger = resource_stockpile_compare parameters = { resource = food }`).
- **Tiers:** several `triggered_modifier`s with thresholds (`count_owned_megastructure = { count >= 3 }`,
  `count_owned_planet = { limit = { is_artificial = yes } count >= 5 }`, `pop_amount_percentage = { percentage >= 0.2 limit = {...} }`).
- **Conditions:** `is_at_war`, `has_deficit = energy`, `has_monthly_income = { resource = food value > 50 }`, `num_rivals`.
- The game can't display live multipliers, so every hook has a `custom_tooltip = <key>_tt` explaining it (checked for loc).
- **Agendas:** a finisher (or, for Megaforge, the adopt tradition) has `unlocks_agenda = agenda_lfg_x`; the agenda's `allow`
  checks that same tradition, `potential` includes
  `has_paragon_dlc = yes`; `modifier` applies while preparing; `effect` runs on launch; `finish_modifier` is a static modifier
  (common/static_modifiers) that lasts 10 years (`COUNCIL_AGENDA_FINISH_MODIFIER_DURATION`). Cost `@lfg_agenda_cost`.
  Loc keys: `council_agenda_<key>_name`, `council_agenda_<key>_desc`, `<finish>`, `<finish>_desc` (checker enforces).
- Avoid ruler traits / new buildings unless needed; they need much more content (traits, gfx, loc) to do well.

## Policies that steer a tradition

Policy options can't scale with game state, so a policy only sets a `policy_flags` flag and the tradition holds the
scaling `triggered_modifier`s keyed on `has_policy_flag` (see `lfg_monument_economy` + `tr_lfg_megaforge_monuments`).
The first option is the default; Monument Economy's is a no-effect `Balanced` option (`policy_flags = {}`), so every
scaling branch is keyed on its own flag.
Policy `category` must be a vanilla one (diplomacy/economy/military/research/society; the checker enforces it).
Loc: `policy_<key>`, `policy_<key>_desc`, and for each option `<name>`, `<name>_name`, `<name>_desc`.

## Modifier names in tooltips

The game names engine modifiers under unpredictable `MOD_COUNTRY_...` keys and economic-category modifiers automatically,
but modifiers it generates **per job / per district** (`pop_<job>_bonus_workforce_mult`, `job_<job>_max_workforce_mult`,
`planet_district_<d>_build_speed_mult`, `district_<d>_max_add`, ...) are only named when vanilla added `mod_<modifier>`.
Unnamed ones show as raw `mod_...` text. The checker flags these (`GENERATED_MODIFIER` in check_mod.py); fix by adding
`mod_<modifier>` to `lfg_modifiers_l_english.yml` in vanilla's wording ("Job Efficiency for [job.GetNamePlural]",
"<District> Build Speed"), or hide a long list in a **static modifier** with `show_only_custom_tooltip = yes` + a summary `custom_tooltip`,
applied from the tradition's `on_enabled` (`add_modifier = { ... days = -1 }`). `show_only_custom_tooltip` is ignored in
tradition modifier blocks (verified in game; the checker rejects it there).
Never redefine a `mod_` key the game or Giga already has (checker enforces).

## Species traits

Predator-only traits: `species_potential_add = { always = no }` + `initial = no` (not pickable / gene-moddable), and tags
`{ <category> organic positive }` where category is one the Evolutionary Predators events roll (pop_growth, pop_output,
leader, habitability, upkeep, or a phenotype tag + `species`), so vanilla `add_random_trait_evopred` can grant it.
Tag `lfg_predator_only` keeps it out of Species Experimentation (its filter excludes that tag). Loc: `trait_<key>`, `_desc`.
Per-pop output goes in `resources = { category = planet_pops_traits produces = { ... } }` (like vanilla trait_notofthisworld).

## Planet-only effects from a tradition

Tradition modifiers are country-wide (they reach every planet). For "only on X planets", use a static planet modifier
kept on the right planets by a hidden monthly event (`on_monthly_pulse_country`) also fired from the tradition's
`on_enabled`, with a country flag so the trigger is cheap and one last run cleans up after the tradition is lost.
Examples: Galactic Destination (`lfg_resorts.1`), Shellworlders (`lfg_shellworlders.1` + `lfg_sync_shellworld_modifier`).
Add every such modifier to `lfg_planet.1` (owner-change cleanup). A count-scaled one is re-added with
`add_modifier = { ... multiplier = <planet variable> }` only when the count changes (see `lfg_sync_arc_neighbours`).
Also **verified in game**: adding our own event to a vanilla situation's `on_monthly` list via a generated override, and
`while = { count = value:<script value> ... }` (Synthetic Fertility's `lfg_synthetic_fertility.1`).
`multiplier = <planet variable>` is **verified in game** (Expand the Resort's `lfg_resort_expansion`, as is its
`multiplier = value:...` decision cost).
Prefer a real planet-class modifier when one exists (e.g. `planet_artificial_max_districts_add`), which is instant.

## Resort and Pleasure Worlds

A Pleasure World (`col_pleasure`, Shroud + `bliss_accord` flag) is a resort colony with another designation. Always
check `has_modifier = resort_colony`, never `has_designation = col_resort`, so Tourism covers both. District
specializations are zones (`common/zones`, sets `resort` / `resort_attraction`); there's no zone-jobs modifier, so zone
bonuses are per-zone overrides (`RESORT_ZONES` in gen_overrides.py).

## Jobs and district specializations

A zone (specialization) is offered in a district's slots by `zone_sets` (`urban` = city slots, which Prison Districts
also use); restrict it with `potential` (planet scope). Jobs come from `triggered_district_planet_modifier = {
job_<key>_add = @scaling_district_1_job }`. A job's icon is `swappable_data.default.icon = <name>`, loaded from
`gfx/interface/icons/jobs/job_<name>.dds` (Giga's files work). Loc: zone `<key>`/`_desc`; job `job_<key>`/`_plural`/`_desc`
(checker enforces). Modifiers the game generates for new jobs/categories (`job_<key>_add`, `planet_<category>_*`) aren't in
modifiers.log until the game has loaded the mod, so don't use them in static modifiers checked against the snapshot.
**Unverified in game:** the new zone, job and economic category.
Also unverified: Transportation's shipments (`lfg_penal_ship_unemployed`: `create_pop_group` on another planet based on a
pop group, then `transfer_pop_amount` with a variable amount). Vanilla resettlement only targets planets with open jobs,
so a destination modifier can't keep pulling pops to a full planet. Also unverified: Idle Hands attrition (`lfg_penal_idle_hands_attrition`): `count_owned_pop_amount` exported in planet
scope, variables on pop groups, and `kill_pop_group = { amount = <variable> }` (vanilla does this in refugee_events.txt).

## Special systems

Spawned from `on_game_start` with a global `event = { ... }` (the checker accepts `event` as an event key) using
`set_spawn_system_batch = begin/end` + `no_scope = { spawn_system = { ... initializer = lfg_x hyperlane = no } }`, like
vanilla's L-Cluster: distances are from the galactic core; galaxy radius is 200/300/400/450/450 (tiny..huge,
`map/setup_scenarios`), checked with `galaxy_size = <size>`. Initializers need `usage_odds = 0` so map generation never
places them. Pre-FTLs: `init_effect = { generate_pre_ftls_on_planet = yes }` (vanilla picks species, age, pops).
**Unverified in game:** pre-FTL generation from an initializer spawned after game start.

## Curated Progress / Shelve edicts

- To shelve a new repeatable (new game or Giga version): find techs with `levels = -1` in game + Giga `common/technology`
  (skip event techs like `tech_repeatable_lcluster_clue`, `tech_cosmogenesis_thesis`), add a `SHELVE` row (edict suffix,
  tech, area, source file, potential trigger = the tech's prerequisite) and a `SHELVE_EFFECTS` entry (what one
  level gives + an evidence string from the tech's `modifier`), regenerate, and update README's table and the
  edict count in `tests/test_check_mod.py`. Techs with `levels = 5` are not repeatables.
- Blocking = `modifier = { factor = 0 has_edict = ... }` in the tech's `weight_modifier` (country scope). It only stops new draws.
- Edict cost/upkeep `multiplier = value:edict_size_effect` (vanilla script value), research upkeep in the tech's area
  (pattern from More Traditions). Loc uses `$<tech key>$`; the checker verifies those keys exist.
- **Unverified in game:** research upkeep on edicts, the inline-script override replacing Giga's, `$tech$` in edict names.

## Steam page: easter eggs stay secret

`workshop_description.txt` must explain every feature **except** the Evolutionary Predators content: the
Inherited Genius trait and the Species Experimentation edict are easter eggs (user's decision). So is the **Lone Tide** special
system: don't mention it (or a hidden/special system) on the Steam page either. Don't mention them,
Evolutionary Predators or subspecies on the Steam page (the Shelve edicts are public); `tests/test_workshop_description.py` enforces it.
The README (private repo) documents them normally. When features change, update the Steam page too.
