# CLAUDE.md

Stellaris 4.5 gameplay mod (requires Gigastructural Engineering 4.5): 6 tradition trees, 7 council agenda definitions (6 agendas), the Evolutionary
Predators edict `lfg_species_experimentation`, the ascension perk
`ap_lfg_curated_progress` + 27 generated Shelve edicts, and generated overrides of 1 situation +
1 district (district_resort) + 8 resort zones + 3 buildings (holomuseums) + 24 repeatable techs + Giga's megastructure-capacity inline script
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
  common/tradition_categories/00_<tree name>_lfg.txt         # 6 trees, one per file (sort order, see below)
  common/traditions/lfg_traditions.txt                       # adopt/finish + 5 traditions per tree
  common/script_values/lfg_script_values.txt                 # lfg_synthetic_fertility_acceleration, lfg_species_split_share
  common/scripted_variables/lfg_scripted_variables.txt       # @lfg_species_split_* tunables (50 / 50 / -2000)
  common/scripted_triggers/lfg_species_split_triggers.txt    # lfg_species_split_eligible (species scope, prev = country)
  common/scripted_effects/lfg_species_split_effects.txt      # lfg_split_species (the split itself)
  common/edicts/lfg_edicts.txt                               # lfg_species_experimentation -> fires lfg_species_split.1
  events/lfg_species_split_events.txt                        # species picker event
  events/lfg_polymath_events.txt                             # Reckless Experimentation lab accident (yearly)
  events/lfg_resorts_events.txt                              # Galactic Destination: resort world modifier + tourist count (monthly)
  events/lfg_shellworlders_events.txt                        # Shellworlders: lfg_shellworld_* modifiers on artificial worlds (monthly)
  common/scripted_effects/lfg_shellworlders_effects.txt      # lfg_sync_shellworld_modifier / _natural_world / lfg_sync_arc_neighbours
  events/lfg_planet_events.txt                               # lfg_planet.1: strip per-planet modifiers on owner change
  events/00_lfg_event_overrides.txt                          # GENERATED (machine_age.4400: Virtuality block); 00_ = loads first
  common/council_agendas/lfg_council_agendas.txt             # 7 agendas, unlocked by tree finishers
  common/static_modifiers/lfg_static_modifiers.txt           # agenda finish modifiers + lfg_lab_accident
  common/on_actions/lfg_on_actions.txt                       # monthly -> lfg_resorts.1 + lfg_shellworlders.1, yearly -> lfg_polymath.1,
                                                             #   colony transfer/ownerless -> lfg_planet.1
  common/decisions/lfg_decisions.txt                         # decision_lfg_expand_resort (resort world, Paradise Unbound)
  common/traits/lfg_traits.txt                               # trait_lfg_inherited_genius (Evolutionary Predators only)
  common/policies/lfg_policies.txt                           # lfg_monument_economy (unlocked by Monument Economy)
  common/ascension_perks/lfg_ascension_perks.txt             # ap_lfg_curated_progress (needs Gigastructural Constructs)
  common/edicts/lfg_shelve_edicts.txt                        # GENERATED Shelve edicts (from SHELVE in gen_overrides.py)
  common/technology/zz_lfg_repeatable_overrides.txt          # GENERATED (24 repeatables: factor 0 while shelved)
  common/inline_scripts/technology/giga_mega_repeatable.txt  # GENERATED whole-file override of Giga's inline script
  common/situations/zz_lfg_situation_overrides.txt           # GENERATED
  common/districts/zz_lfg_district_overrides.txt             # GENERATED (district_resort: Hospitality Academies jobs)
  common/buildings/zz_lfg_building_overrides.txt             # GENERATED (3 holomuseums: Holo-Museums bonus)
  common/zones/zz_lfg_zone_overrides.txt                     # GENERATED (8 resort zones: Hospitality Academies +50% jobs)
  interface/lfg_traditions.gfx                               # sprites -> vanilla .dds (no art ships)
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

1. `common/tradition_categories/00_<English tree name>_lfg.txt` (one tree per file; e.g. "The Grand Tour" ->
   `00_grand_tour_lfg.txt`). The traditions window lists trees in load order = file name order, so this sorts the tree
   alphabetically among vanilla's `00_<tree>.txt` regular trees instead of after the `01_*` ascension trees (More
   Traditions does the same). The checker enforces the name. Then `tradition_lfg_<name> = { desc, potential, tree_template = "tree_21_11",
   adoption_bonus = "tr_lfg_<name>_adopt", finish_bonus = "tr_lfg_<name>_finish", traditions = { 5 keys in slot order }, ai_weight }`.
   Include the `@ap_pending_tradition_suppress` modifier, as vanilla does.
2. `common/traditions/lfg_traditions.txt`: `_adopt` (optional `possible`), `_finish` (`ascension_perks_add = 1`), 5 traditions.
   With `tree_21_11`, slot 4 needs `possible = { has_tradition = <slot1> has_tradition = <slot2> }` and slot 5 needs `<slot3>`.
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
5. Never put Steam credentials in the repo or CI. `PUBLISH_SKIP_TESTS=1` exists only so `test_publish.py` doesn't recurse.

## Species Experimentation edict - how it works and what's unverified

- Edict `lfg_species_experimentation` (loc `edict_<key>`; potential: `has_origin = origin_evolutionary_predators` +
  `has_tradition = tr_mutation_finish`; allow: any owned species passes
  `lfg_species_split_eligible`) -> `effect` fires `lfg_species_split.1`.
- Why an edict and a popup: `button_effects` in the species screen run in **country** scope (the selected species isn't
  available), and the user chose an edict over overriding UIOD's species window. Picking happens in the event (4 random
  eligible candidates saved as `event_target:lfg_split_candidate_1..4`, "Show others" re-fires the event).
- `lfg_split_species` (country scope, needs `event_target:lfg_split_source`): `add_resource = { society_research = -2000 }`
  (research isn't stockpiled; same as vanilla `paragon.270`), then `while` 50x: `modify_species` with
  `change_scoped_species = no` + `add_random_species_trait` (filter copied from vanilla `add_random_trait_evopred`), then
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
`multiplier = <planet variable>` is **verified in game** (Expand the Resort's `lfg_resort_expansion`, as is its
`multiplier = value:...` decision cost).
Prefer a real planet-class modifier when one exists (e.g. `planet_artificial_max_districts_add`), which is instant.

## Resort and Pleasure Worlds

A Pleasure World (`col_pleasure`, Shroud + `bliss_accord` flag) is a resort colony with another designation. Always
check `has_modifier = resort_colony`, never `has_designation = col_resort`, so The Grand Tour covers both. District
specializations are zones (`common/zones`, sets `resort` / `resort_attraction`); there's no zone-jobs modifier, so zone
bonuses are per-zone overrides (`RESORT_ZONES` in gen_overrides.py).

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
Inherited Genius trait and the Species Experimentation edict are easter eggs (user's decision). Don't mention them,
Evolutionary Predators or subspecies on the Steam page (the Shelve edicts are public); `tests/test_workshop_description.py` enforces it.
The README (private repo) documents them normally. When features change, update the Steam page too.
