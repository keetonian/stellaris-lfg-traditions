# LFG Traditions

A Stellaris **4.5** mod for **Gigastructural Engineering & More (4.5)** games that adds:

- **6 tradition trees**, each available only to fitting empires (origin, empire type, technology).
- **1 civic, Pampered Masters**: a "reverse Rogue Servitor", where biological masters are served by robots.
- **2 balance overrides**: the civic blocks Cybernetic/Synthetic ascension, and Synthetic Fertility's situation speeds up every year.

This is a gameplay mod (it adds `common/` files), so it **changes the game checksum**. Everyone in a multiplayer game needs it.

> **Status: draft.** The balance numbers are a first pass and haven't been playtested. Everything is checked statically
> (see [Verification](#verification)), but in-game testing is still to do.

## Requirements

- Stellaris 4.5.x
- [Gigastructural Engineering & More (4.5)](https://steamcommunity.com/sharedfiles/filedetails/?id=1121692237). Required: the Megaforge tree uses its supertensiles, techs and origins.
- Recommended: [A Lot of Traditions - 24 Tradition Slots](https://steamcommunity.com/sharedfiles/filedetails/?id=3089158981).
  Vanilla allows 7 trees in total, and this mod adds 6 more options. Compatible with Expanded Stellaris Traditions and More Traditions (no shared keys).

Load order: after Gigastructural.

## Tradition trees

All trees use the vanilla `tree_21_11` layout (like Supremacy): three traditions on top, then
**slot 4 requires slots 1 + 2** and **slot 5 requires slot 3**. Each finisher grants **+1 ascension perk**, as in vanilla.
Every tree trades a clear buff for a clear nerf.

### Megaforge Doctrine: megastructures over the normal economy
**Who:** any non-nomadic empire. **Adopt requires:** *Supertensile Materials* (Giga) or *Mega-Engineering* research.

Supertensile bonuses apply only when Gigastructural's job-based construction mode is on (global flag
`giga_buildcap_j`, the default "Giga's experience" preset). In other build modes they become plain megastructure
cost/upkeep reductions instead, marked "else" below.

| Tradition | Buffs | Nerfs |
|---|---|---|
| Adopt | Megastructure build speed +10%; supertensile output +15% (else megastructure cost −5%) | Minerals −5%, energy −5% |
| 1. Megaengineer Guilds | Megaengineer output +15%, upkeep −10% (else megastructure cost −5%) | Worker output −5% |
| 2. Supertensile Lattices | Megastructure supertensile upkeep −20%, supertensile storage +1000 (else megastructure upkeep −10%) | Trade −5% |
| 3. Grand Works Priority | Megastructure build speed +15% | Planet building cost +10%, building speed −10% |
| 4. Orbital Foundries | Supertensile output +15% (else megastructure cost −10%) | Minerals −5% |
| 5. Monument Economy | Megastructure output +10% | Energy −5% |
| Finish | Megastructure build speed +10% | |

### Leisure Society: civilians over workers
**Who:** regular (non-gestalt) empires, since the civilian job doesn't exist for gestalts.

| Tradition | Buffs | Nerfs |
|---|---|---|
| Adopt | Civilian happiness +10%, civilian unity +0.1 | Worker happiness −5% |
| 1. Patronage of the Arts | Civilian unity +0.25 | |
| 2. Leisure Markets | Civilian trade +0.25 | |
| 3. Shorter Shifts | Happiness +5% | Worker output −10% |
| 4. Citizen Dividend | Civilian political power +25% | Worker political power −25% |
| 5. Amenity Culture | Amenities +10% | Worker consumer goods upkeep +0.05 |
| Finish | Civilian unity +0.25 | |

### Attendant Robotics: fewer, better robots that serve organics
**Who:** regular empires that are not individualist machines, synthetic, or on the cybernetic path. **Adopt requires:** *Robotic Workers*.
This is the companion tree for **Pampered Masters**: entries marked ★ give extra bonuses with that civic.

| Tradition | Buffs | Nerfs |
|---|---|---|
| Adopt | Robot workforce +5% | Robot assembly −5% |
| 1. Domestic Protocols | Servant workforce +25%, organic amenity usage −5% | |
| 2. Quality over Quantity | Robot workforce +10% | Robot assembly −10% |
| 3. Licensed Roboticists | Robot upkeep −15% | Roboticist jobs −10% |
| 4. Personal Valets | Biological happiness +5% (★ another +5%) | |
| 5. Household AI | Robot amenity usage −25% (★ robot workforce +10%) | |
| Finish | Robot workforce +5% (★ organic workforce +10%) | |

### Overclocked Network: complex drones over simple drones
**Who:** Machine Intelligence (gestalt machine) empires only. This is the gestalt counterpart to Leisure Society.

| Tradition | Buffs | Nerfs |
|---|---|---|
| Adopt | Complex drone output +5% | Simple drone output −5% |
| 1. Priority Threads | Complex drone output +10% | Simple drone output −5% |
| 2. Coolant Loops | Job upkeep −5% | |
| 3. Burst Assembly | Pop assembly +10% | Simple drone output −5% |
| 4. Heuristic Cores | Research speed +5% | Minerals −5% |
| 5. Redline | Complex drone workforce +10% | Simple drone workforce −10% |
| Finish | Complex drone output +5% | |

### Shellworlders: life on artificial worlds
**Who:** empires with an artificial-world origin (Giga: Frameworld, Decaying Birch World, Great Ring, Interstellar Ring,
Alderson Disk; vanilla: Shattered Ring, Void Dwellers), or anyone after researching *Orbital Habitats* or *Ring World*.

| Tradition | Buffs | Nerfs |
|---|---|---|
| Adopt | Habitat cost −10% | Organic growth −5% |
| 1. Compact Living | Housing usage −5% | |
| 2. Artificial Gravity | Stability +3 | |
| 3. Frame Engineering | Frameworld cost −15%, habitat cost −10% | |
| 4. Closed Ecology | Amenities +5% | Organic growth −5% |
| 5. Ring Cities | Megastructure build speed +10%, housing usage −5% | |
| Finish | Stability +2 | |

### Stellar Harvest: starlight over farms and mines
**Who:** any non-nomadic empire. **Adopt requires:** *Dyson Swarm* (Machine Age) or *Dyson Sphere*.

| Tradition | Buffs | Nerfs |
|---|---|---|
| Adopt | Megastructure energy output +10% | Food −5% |
| 1. Collector Arrays | Energy +5% | Minerals −5% |
| 2. Photonic Agriculture | Megastructure upkeep −10% | |
| 3. Star Lifting | Megastructure output +5% | Minerals −5% |
| 4. Energy Credits | Trade +10% | Food −5% |
| 5. Stellar Priority | Megastructure build speed +15% | |
| Finish | Megastructure energy output +10% | |

## Civic: Pampered Masters

"Our robots do the work so that our people do not have to." This is the reverse of Rogue Servitor: an
**individualist, biological** empire whose robots serve the organics. Robots are precious and few, and the masters are comfortable and lazy.

- **Who can take it:** non-gestalt empires whose species is not Machine or Mechanical. **Not** with the origins Cybernetic Creed,
  Synthetic Fertility, Mechanists or Unplugged, the civics Augmentation Bazaars or Permanent Employment, or Fanatic Spiritualist ethics.
- **Upsides:** biological happiness +10%, organic amenity usage −20%, robot workforce +20%, servant (domestic robot) workforce +25%.
- **Strong downsides:** organic workforce **−20%**, robot assembly **−40%**, roboticist jobs −25%, roboticist alloy upkeep +1,
  worker consumer goods upkeep +0.1.
- **No Cybernetic or Synthetic ascension.** *The Flesh is Weak* and *Synthetic Evolution* show as unavailable, with the reason
  "Incompatible with the Pampered Masters civic". Psionic and Genetic ascension remain available.
- Pairs with the **Attendant Robotics** tree. Tip: give your robots *Domestic Protocols* and Servitude citizenship so they take the Servant job.

## Overrides of vanilla content

These replace two vanilla definitions. Other mods that change the same definitions will conflict; whichever loads last wins.

| Vanilla definition | Change |
|---|---|
| Ascension perks `ap_the_flesh_is_weak`, `ap_synthetic_evolution` | Added requirement: not Pampered Masters |
| Situation `situation_synthetic_fertility_digitization` (the Synthetic Fertility origin's "uploading" situation) | Monthly progress **+1 for every year since game start**, on top of the vanilla base of 15 (year 10: 25/month). It completes noticeably sooner. |

The override files are **generated** from the installed game by `tools/gen_overrides.py`, so they're vanilla text
plus clearly marked `# LFG: added` lines.

## Install (local)

```sh
scripts/install.sh
```

This copies `mod/` to `~/Documents/Paradox Interactive/Stellaris/mod/lfg_traditions/` and writes `lfg_traditions.mod` for the launcher.
It installs a **local dev copy**: the name gets a ` [LOCAL DEV]` suffix and `remote_file_id` is removed, so the
launcher lists it separately from the Workshop version you're subscribed to. Enable one or the other, not both.
`mod/descriptor.mod` itself is never changed. `RELEASE=1 scripts/install.sh` installs an exact copy instead; use that only
for a launcher upload.
Enable the mod after Gigastructural.

## Verification

```sh
scripts/verify.sh                    # 49 tests + static check
scripts/verify.sh --require-sources  # before a release: fail if game/Giga files are missing
```

`tools/check_mod.py` parses every mod file and fails on:
- **Files:** unexpected files in `mod/`, parse errors or unbalanced braces, descriptor problems, a non-PNG or oversized thumbnail.
- **Localisation:** missing BOM or `l_english:` header, malformed lines, duplicate keys, unbalanced `§` colour codes, keys without an `lfg` prefix.
- **Tree structure:** each tree has exactly 5 traditions plus adopt/finish, every tradition belongs to exactly one tree,
  prerequisites stay inside their tree and match the layout (slot 4 ← 1+2, slot 5 ← 3), and `tree_template` exists.
- **Missing localisation:** for every tree, tradition (`name`/`_desc`/`_delayed`), civic, and any `lfg` key referenced by `desc`/`text`/`fail_text`/…
- **Sprites:** the 4 category sprites per tree, a `GFX_<tradition>` per tradition, and that every texture file exists in the game.
- **Modifiers:** every name exists in the game's modifier list (local `modifiers.log`, or the bundled
  `tools/data/modifiers_4.5.txt.gz` snapshot in CI), and every value is numeric.
- **References:** every `has_technology`/`has_origin`/`has_valid_civic`/`has_ethic`/`has_tradition`, civic `origin`/`civics`/`ethics`
  value and `@variable` exists in the game, Gigastructural or this mod.
- **Overrides:** the vanilla override files match a fresh `tools/gen_overrides.py` run, and the script values they use exist.

CI (`.github/workflows/verify.yml`) runs the tests and the checks that don't need game files on every push.

**Still to test in game:**
- Each tree appears only for the right empires.
- The civic is blocked for cybernetic/machine/synthetic setups, and the two ascension perks show the new requirement.
- A Synthetic Fertility empire's situation tooltip shows the yearly line and the rate grows each year.
- `~/Documents/Paradox Interactive/Stellaris/logs/error.log` has no `lfg` errors.

## Publish to the Steam Workshop

`scripts/publish.sh` checks the mod and uploads it with [steamcmd](https://developer.valvesoftware.com/wiki/SteamCMD)
(the same setup as `stellaris-gigas-ehof-fix`):

```sh
brew install --cask steamcmd                          # once
DRY_RUN=1 scripts/publish.sh                          # show exactly what would be uploaded; no login
STEAM_USER=<steam account name> scripts/publish.sh "Changelog line"
```

- **Refuses to upload** unless the full test suite and `check_mod.py --require-sources` pass (so the game and Giga must be
  installed), and unless `mod/` is committed (`ALLOW_DIRTY=1` overrides).
- Uploads only the contents of `mod/`, minus `.DS_Store`.
- **First run** (no `remote_file_id` in `mod/descriptor.mod`): creates a **private** Workshop item titled from the descriptor, with
  `workshop_description.txt` as its description. It then appends `remote_file_id` to `mod/descriptor.mod`.
  Commit that line, and add **Gigastructural Engineering** as a *Required item* on the Workshop page.
- **Later runs** update the same item with the files and a change note (default `v<version> (<commit>)`). Bump `version` in
  `mod/descriptor.mod` first. `VISIBILITY=0|1|2|3` (public / friends-only / private / unlisted) and `SYNC_DESCRIPTION=1`
  also update those on Steam.
- `STEAM_USER` is your Steam **account name** (the login name, not your profile name). steamcmd asks for the password and
  Steam Guard code once, then caches the login. Nothing is stored in this repo.
- Double quotes in the description or change note are turned into “typographic quotes”, because steamcmd's VDF parser has no escapes.

Alternative: run `RELEASE=1 scripts/install.sh` (so the upload isn't named "[LOCAL DEV]"), then use the Paradox launcher's **Upload mod** and copy the `remote_file_id` it writes
into `mod/descriptor.mod`.

Publishing to the Workshop is local-only on purpose: CI would need your Steam credentials, and the strict checks need the game installed.

## Ideas for later

- Custom icons and art instead of reused vanilla icons.
- `tradition_swap` variants with gestalt- and nomad-specific names and text.
- Planet-level effects for Shellworlders that apply only on artificial worlds (needs scripted planet modifiers).
- A start-of-game effect for Pampered Masters that gives the founder robots *Domestic Protocols* and Servitude citizenship.
