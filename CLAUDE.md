# CLAUDE.md

Stellaris 4.5 gameplay mod (requires Gigastructural Engineering 4.5): 6 tradition trees, the civic
`civic_lfg_pampered_masters`, and generated overrides of 2 ascension perks + 1 situation. User-facing docs and the
full effect tables are in README.md. **Keep README's tables in sync when you change numbers.**

## Commands

```sh
scripts/verify.sh                         # unittest (tests/) + tools/check_mod.py; run after every change
scripts/verify.sh --require-sources       # also fail if game/Giga files are missing (do before releases)
python3 -I tools/gen_overrides.py         # regenerate vanilla overrides (after game updates)
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
  common/tradition_categories/lfg_tradition_categories.txt   # 6 trees
  common/traditions/lfg_traditions.txt                       # adopt/finish + 5 traditions per tree
  common/governments/civics/lfg_civics.txt                   # Pampered Masters
  common/script_values/lfg_script_values.txt                 # lfg_synthetic_fertility_acceleration
  common/ascension_perks/zz_lfg_ascension_path_overrides.txt # GENERATED
  common/situations/zz_lfg_situation_overrides.txt           # GENERATED
  interface/lfg_traditions.gfx                               # sprites -> vanilla .dds (no art ships)
  localisation/english/lfg_*_l_english.yml                   # UTF-8 BOM
tools/pdx.py          # small Paradox-script parser
tools/check_mod.py    # static verification (see README "Verification")
tools/gen_overrides.py
tools/data/modifiers_4.5.txt.gz       # modifier-name snapshot used when modifiers.log is absent (CI)
tests/                # unittest; mutation tests copy mod/, break one thing, expect a specific failure;
                      # test_publish.py dry-runs publish.sh (needs game + Giga, skipped in CI);
                      # test_install.py checks the [LOCAL DEV] / RELEASE=1 installs
workshop_description.txt   # Steam BBCode description (sent on first upload or with SYNC_DESCRIPTION=1)
```

## Rules

- **Prefix everything** `lfg`: `tradition_lfg_*`, `tr_lfg_*`, `civic_lfg_*`, `lfg_*` (script values, loc). Other installed
  mods use `tr_est_*`, `tr_mt_*`, `tr_macroengineering_*`, `tr_gigaengineering_*`, `tr_gigabulwark_*`. Never redefine vanilla or Giga keys
  except through `tools/gen_overrides.py`. The checker enforces prefixes.
- **Never hand-edit the `zz_lfg_*` override files.** Change `OVERRIDES` / the snippets in `tools/gen_overrides.py` and regenerate.
  They are vanilla text plus `# LFG: added` lines. `zz_` makes them load after vanilla so they replace it.
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
- **Civic `possible` can't see ascension perks.** Blocking mid-game ascension requires overriding the perk (that's why
  `gen_overrides.py` exists). Put the block in the perk's `possible` with a `custom_tooltip`/`fail_text` so it shows greyed out with a reason.
- **Loc** files must be UTF-8 **with BOM**, start with `l_english:`, one-space indent, `key:0 "text"`. Each tradition needs
  `key`, `key_desc`, `key_delayed`; each tree `tradition_lfg_x` + `_desc`; the civic `civic_x` + `_desc` + the `description`/
  `negative_description` keys. Balance every `§Y…§!` colour code.

## How the pieces connect (adding a tree)

1. `common/tradition_categories/lfg_tradition_categories.txt`: `tradition_lfg_<name> = { desc, potential, tree_template = "tree_21_11",
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
   `tests/test_check_mod.py::test_mod_has_six_trees_and_a_civic`.

## Sources (macOS)

- Game: `~/Library/Application Support/Steam/steamapps/common/Stellaris` (version in `launcher-settings.json`, currently v4.5.2)
- Giga: `~/Library/Application Support/Steam/steamapps/workshop/content/281990/1121692237`
- Modifier list: `~/Documents/Paradox Interactive/Stellaris/logs/script_documentation/modifiers.log` (regenerated by the
  game's `script_docs` console command; it includes modifiers from the mods loaded at the time)
- Overridden vanilla definitions: `common/ascension_perks/00_ascension_paths.txt` (`ap_the_flesh_is_weak`,
  `ap_synthetic_evolution`), `common/situations/08_machine_age_situations.txt` (`situation_synthetic_fertility_digitization`)

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
