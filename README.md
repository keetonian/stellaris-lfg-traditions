# LFG Traditions

A Stellaris **4.5** mod for **Gigastructural Engineering & More (4.5)** games that adds:

- **8 tradition trees**, each with a hook that scales with your game state, available only to fitting empires.
- **8 council agendas** unlocked by the trees.
- **1 civic, Pampered Masters**: a "reverse Rogue Servitor", where biological masters are served by robots.
- **1 edict, Species Experimentation** (Evolutionary Predators, after finishing Mutation): half of a secondary species dies, the rest splits into 50 random-trait subspecies.
- **2 balance overrides**: the civic blocks Cybernetic/Synthetic ascension, and Synthetic Fertility's situation speeds up every year.

This is a gameplay mod (it adds `common/` files), so it **changes the game checksum**. Everyone in a multiplayer game needs it.

> **Status: draft.** The balance numbers are a first pass and haven't been playtested. Everything is checked statically
> (see [Verification](#verification)), but in-game testing is still to do.

## Requirements

- Stellaris 4.5.x
- [Gigastructural Engineering & More (4.5)](https://steamcommunity.com/sharedfiles/filedetails/?id=1121692237). Required: the Megaforge tree uses its supertensiles, techs and origins.
- Recommended: [A Lot of Traditions - 24 Tradition Slots](https://steamcommunity.com/sharedfiles/filedetails/?id=3089158981).
  Vanilla allows 7 trees in total, and this mod adds 8 more options. Compatible with Expanded Stellaris Traditions and More Traditions (no shared keys).

Load order: after Gigastructural.

## Tradition trees

Every tree has a **hook**: bonuses that scale with or depend on the state of your game, so the tree changes how you
play rather than just adding percentages. Hooks are marked ⚙. Most finishers also unlock a **council agenda**
(see [Council agendas](#council-agendas)). All trees use the vanilla `tree_21_11` layout: slots 1–3 on top,
**slot 4 requires 1 + 2**, **slot 5 requires 3**. Every finisher grants **+1 ascension perk**.

### Megaforge Doctrine: megastructures over the normal economy
**Who:** non-nomadic. **Adopt requires:** *Supertensile Materials* (Giga) or *Mega-Engineering*.
**Hook:** megastructure output grows with how many megastructures you own. **Agenda (on adoption):** The Great Project.
Supertensile bonuses need Gigastructural's job-based build mode (`giga_buildcap_j`, the default); otherwise they become megastructure cost/upkeep reductions ("else").

| Tradition | Effect |
|---|---|
| Adopt | Megastructure build speed +10%; supertensiles +15% (else megastructure cost −5%) · unlocks agenda **The Great Project** |
| 1. Megaengineer Guilds | Megaengineer output +15% · megaengineer upkeep +15% (else megastructure build speed +15%) |
| 2. Supertensile Lattices | Supertensile upkeep −20%, supertensile storage +10,000 (else megastructure upkeep −15% and resource storage +100,000) |
| 3. Grand Works Priority | Megastructure build speed +20%, infrastructure (building and district) build speed +20% · infrastructure cost +30% |
| 4. Orbital Foundries | Supertensiles Technicians +0.25 supertensiles and +1 alloy upkeep each, Megaconstruction Directors +1.5 supertensiles and +3 alloy upkeep each (else megastructure cost −10%, alloys −5%) · minerals −10% |
| 5. Monument Economy ⚙ | Unlocks the **Monument Economy** policy. Per megastructure owned (kilostructures count, ruins don't; no cap): *Balanced* (default) no effect, *Monuments First* megastructure output +1% · job output −0.5%, or *People First* job output +0.5% · megastructure output −1%. Monthly supertensiles +10 |
| Finish | +1 Megaconstruction Logistics Hub limit (else +1 megastructure build limit) |

### Attendant Robotics: fewer, better robots that serve organics
**Who:** only empires with the **Pampered Masters** civic. **Adopt requires:** *Robotic Workers*. **Hook:** robots excel only while rare.

| Tradition | Effect |
|---|---|
| Adopt | Robot workforce +5% · robot assembly −5% |
| 1. Domestic Protocols | Servant workforce +25%, organic amenity usage −5% |
| 2. Quality over Quantity ⚙ | Robots under 15% of pops: robot workforce +20%; over 35%: −10% · robot assembly −10% |
| 3. Licensed Roboticists | Robot upkeep −15% · roboticist max workforce −10% |
| 4. Personal Valets | Biological happiness +10% |
| 5. Household AI | Robot amenity usage −25%, robot workforce +10% |
| Finish | **Doubles the civic's pampering:** biological happiness +10%, organic amenity usage −20%, servant workforce +25% |

### Overclocked Network: complex drones over simple drones
**Who:** Machine Intelligence only. **Hook:** runs hot: an energy deficit throttles it, war pushes it. **Agenda:** Overclock Protocol.

| Tradition | Effect |
|---|---|
| Adopt | Complex drone output +5% · simple drone output −5% |
| 1. Priority Threads | Complex drone output +10% · simple drone output −5% |
| 2. Coolant Loops ⚙ | Job upkeep −10% · during an energy deficit, complex drone output −25% |
| 3. Burst Assembly | Pop assembly +10% · simple drone output −5% |
| 4. Heuristic Cores | Research speed +5%, +1 research option · minerals −5% |
| 5. Redline ⚙ | Complex drone workforce +10% (+10% more and ship fire rate +5% at war) · simple drone workforce −10% |
| Finish | Unlocks agenda **Overclock Protocol** |

### Shellworlders: life on artificial worlds
**Who:** artificial-world origins (Giga: Frameworld, Decaying Birch World, Great Ring, Interstellar Ring, Alderson Disk;
vanilla: Shattered Ring, Void Dwellers), or after *Orbital Habitats* / *Ring World*. **Hook:** grows with artificial worlds owned.

| Tradition | Effect |
|---|---|
| Adopt | Habitat cost −10% · organic growth −5% |
| 1. Compact Living | Housing usage −5% |
| 2. Artificial Gravity | Stability +3 |
| 3. Frame Engineering | Frameworld cost −15%, habitat cost −10% |
| 4. Closed Ecology | Amenities +5% · organic growth −5% |
| 5. Ring Cities | Megastructure build speed +10%, housing usage −5% |
| Finish ⚙ | 2+ artificial worlds: stability +2; 5+: +2 more and housing −5%; 10+: +2 more, housing −5% more, megastructure build speed +10% |

### Polymath Commons: research from everyone
**Who:** any empire. **Hook:** research scales with species and rivals; experiments go wrong. **Agenda:** Eureka Season.

| Tradition | Effect |
|---|---|
| Adopt | Research speed +5% · researcher upkeep +5% |
| 1. Many Minds ⚙ | Research speed +1% per species in the empire (max +30%) |
| 2. Rival Laboratories ⚙ | Research speed +4% per rival (max +16%); −5% with no rivals |
| 3. Open Journals | Research speed +10% · diplomatic weight −10% |
| 4. Reckless Experimentation ⚙ | Research output from jobs +15% (physics, society, engineering) · each year on a random colony: 5% chance of a **Lab Accident** (stability −10, researcher output −25% there for 5 years) and 15% chance of a **Lab Breakthrough** (stability +5, researcher output +25% there for 5 years) |
| 5. Interdisciplinary Seminars | +1 research option, scientist cap +1 |
| Finish | Anomaly discovery chance +15% · unlocks agenda **Eureka Season** |

### Granary Kings: the food stockpile is political power
**Who:** empires whose **main species eats food** (biological species, voidlings included; not lithoids, machines or robots). Hives get their own description. **Hook:** your food stockpile and income drive the bonuses.
**Agendas:** Feast of Plenty (on adoption), The Harvest Tithe (finisher).

| Tradition | Effect |
|---|---|
| Adopt | Food storage +5000, farmer output +5% · unlocks agenda **Feast of Plenty** |
| 1. Tithe Barns ⚙ | 5,000+ food stored: stability +3, unity +5% · under 500: stability −5 |
| 2. Seed Vaults ⚙ | Unity +1% per 5,000 stored food (max +20%) |
| 3. Bountiful Fields | Farmer output +10% |
| 4. Grain Reserves | Food storage +100,000 · pop food upkeep +100% |
| 5. Harvest Courts ⚙ | Worker political power +25% · specialist political power −25% · while food income is positive: influence +10% |
| Finish ⚙ | **Bumper Crops:** organic growth +1% per 1,000 monthly food income (no cap; doubled during **Feast of Plenty**) · unlocks agenda **The Harvest Tithe** |

### Galactic Broadcast: entertainment for the whole galaxy
**Who:** non-gestalt (gestalts have no entertainers). **Hook:** scales with the empires you know and your commercial pacts; war is prime time; doubles your holomuseums. **Agenda:** Gala Season.

| Tradition | Effect |
|---|---|
| Adopt ⚙ | Trade +1% per empire in contact (max +20%), entertainer output +5% |
| 1. Holo-Museums | Every Grand Archive holomuseum you own is twice as effective: specimen bonus doubled, and its planet's entertainers get its +0.25 unity and +0.25 research again (generated building override) |
| 2. Celebrity Council | Council agenda speed +15%, entertainer unity +0.25 |
| 3. Propaganda Serials | Diplomatic weight +10% · government ethic attraction −15% |
| 4. Ratings War ⚙ | Envoys harming relations +50% · while at war: war exhaustion gain −20%, entertainer output +20% |
| 5. Syndication Deals ⚙ | Per commercial pact (no cap): entertainers +0.5 trade per 100 entertainers · +1 envoy, envoys improving relations +25% · researcher output −5% |
| Finish | Unlocks agenda **Gala Season** |

### The Grand Tour: resort worlds as showpieces
**Who:** regular empires. **Adopt requires:** *Resort Colonies*. **Hook:** an empire can only have **one** resort world, so bonuses scale with how built-up it is: per 100 Resort Workers employed (no cap).
**Agenda (on adoption):** Grand Tour Season. Resort Workers share the entertainer category, so entertainer bonuses (e.g. Galactic Broadcast) also boost them.

| Tradition | Effect |
|---|---|
| Adopt | Resort Worker workforce +10%, resort district build speed +25% · unlocks agenda **Grand Tour Season** |
| 1. Hospitality Academies | Each **Accommodation District** gives +150 Resort Worker jobs (+50%; via a generated `district_resort` override, see below) |
| 2. Package Holidays ⚙ | Per 100 Resort Workers (no cap): unity +0.5%, amenity usage −0.25% |
| 3. Paradise Unbound | Each Accommodation District adds +0.5 max districts to the resort world · unlocks the **Expand the Resort** decision · +1 max Accommodation District, resort district build speed +25% |
| 4. Tourist Traps | Resort Worker workforce +15% · entertainer/resort worker consumer goods upkeep +0.5 |
| 5. Galactic Destination ⚙ | Per 100 Resort Workers (no cap): trade +0.5%, diplomatic weight +0.5% |
| Finish | Resort Worker workforce +10% |

**Growing the resort world** (resort worlds start with −25% max districts, and an empire can only have one):
- **Self-growth:** with Paradise Unbound, every Accommodation District adds +0.5 max districts to its planet, so
  building makes room for more. Because each district adds less than one slot, it converges: about double the normal count at most.
- **Expand the Resort** (planet decision on the resort world, unlocked by Paradise Unbound): 1 year to enact,
  +2 max districts each time, up to 5 times (+10). Cost: 100 influence each time, plus 500 alloys, 500 minerals and
  1,000 unity, rising by that much again with each expansion (5th: 2,500 / 2,500 / 5,000). If the planet ever stops
  being a resort world, the expansions it already has stay.

## Council agendas

Unlocked by finishing the matching tree (The Great Project: by adopting Megaforge). Requires the Galactic Paragons DLC, like all vanilla agendas. The council
prepares an agenda over time; when launched, its effect lasts **10 years**.

| Agenda | Tree | While preparing | Launch / 10-year effect |
|---|---|---|---|
| The Great Project | Megaforge (on adoption) | Megastructure build speed +5% | With supertensiles on: supertensile output +25%, megastructure build speed +33%, cost −10% · worker output −10%. With supertensiles off (separate version, same name): build speed +33%, cost −20% · worker output −10% |
| Overclock Protocol | Overclocked Network | Complex drone output +3% | Complex drone output +20% · simple drone output −10%, job upkeep +10% |
| Eureka Season | Polymath | Research speed +3% | Research speed +20% · stability −5 |
| Feast of Plenty | Granary (on adoption) | Farmer output +5% | For 10 years: doubles the finisher's Bumper Crops (another +1% organic growth per 1,000 monthly food income) |
| The Harvest Tithe | Granary | Farmer output +5% | On launch, if you have 3,000 food: −3,000 food, +150 influence, +2,000 unity. Then food +10%, stability +2 |
| Gala Season | Galactic Broadcast | Entertainer output +5% | Happiness +10%, unity +10% · trade −10% |
| Grand Tour Season | The Grand Tour (on adoption) | Resort Worker workforce +5% | Happiness +10%, trade +15%, Resort Worker workforce +25% · worker output −5% |

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

## Edict: Species Experimentation (Evolutionary Predators)

Subject one of your secondary species to brutal experiments: **half of it dies**, and the survivors are split into
**50 subspecies**, each with **one extra random positive organic trait**, with the population divided evenly between them.

- **Who:** empires with the **Evolutionary Predators** origin that have **finished the vanilla Mutation tradition tree**.
  The edict is hidden until then.
- **Requires:** a species that is **not your main species or any of its subspecies**, with at least **100 pops** (raw population, not 100-pop units).
  Greyed out until one qualifies.
- **Cost:** **2000 society research**, charged when you pick the species (deducted from current research progress, like vanilla events).
- **How it works:** activating the edict opens a popup listing up to 4 eligible species ("Show other species" re-rolls).
  Picking one kills 50% of every pop group of that species, then divides the rest 1/50, 1/49, … 1/1 so the shares come
  out equal. Small pop groups round, so some subspecies may end up with fewer pops.
- **Traits:** positive, organic, and not special/cybernetic/presapient/drawback/genetic-ascension (like the origin's own mutations).
- Numbers (50 subspecies, 100 pops, −2000 research) are in `mod/common/scripted_variables/lfg_scripted_variables.txt`.

**Unverified:** the most script-heavy part of the mod; test on a save you don't mind losing.

## Species trait: Inherited Genius (Evolutionary Predators only)

| Trait | Cost | Effect |
|---|---|---|
| **Inherited Genius** | 2 | +0.3 physics, society and engineering research per 100 pops of the species |

- Can't be picked at species creation or added with gene modding. Only the **Evolutionary Predators** origin's random
  trait events can grant it (it's in their "pop output" category, alongside vanilla traits).
- Never given by **Species Experimentation** (its random trait filter skips it).

## Overrides of vanilla content

These replace two vanilla definitions. Other mods that change the same definitions will conflict; whichever loads last wins.

| Vanilla definition | Change |
|---|---|
| Ascension perks `ap_the_flesh_is_weak`, `ap_synthetic_evolution` | Added requirement: not Pampered Masters |
| Buildings `xeno_geology_holomuseum`, `aesthetic_wonders_holomuseum`, `galactic_history_holomuseum` | Added: their entertainer unity/research bonus again while the owner has Holo-Museums |
| District `district_resort` (Accommodation District) | Added: +150 Resort Worker jobs per district (Hospitality Academies) and +0.5 max districts per district (Paradise Unbound) |
| Situation `situation_synthetic_fertility_digitization` (the Synthetic Fertility origin's "uploading" situation) | Monthly progress **+1 for every year since game start**, on top of the vanilla base of 15 (year 10: 25/month). It completes noticeably sooner. |

The override files are **generated** from the installed game by `tools/gen_overrides.py`, so they're vanilla text
plus clearly marked `# LFG: added` lines.

## Install (local)

```sh
scripts/install.sh
```

This copies `mod/` to `~/Documents/Paradox Interactive/Stellaris/mod/lfg_traditions/` and writes `lfg_traditions.mod` for the launcher.
It installs a **local dev copy**: the name gets a `[LOCAL DEV] ` prefix and `remote_file_id` is removed, so the
launcher lists it separately from the Workshop version you're subscribed to. Enable one or the other, not both.
`mod/descriptor.mod` itself is never changed. `RELEASE=1 scripts/install.sh` installs an exact copy instead; use that only
for a launcher upload.
Enable the mod after Gigastructural.

## Verification

```sh
scripts/verify.sh                    # 71 tests + static check
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
- **Overrides:** the vanilla override files match a fresh `tools/gen_overrides.py` run.
- **Modifier names:** every job/district-generated modifier shown in a tooltip has a name in the game, Giga or `lfg_modifiers_l_english.yml`
  (otherwise the tooltip shows the raw `mod_...` key), unless it's hidden behind `show_only_custom_tooltip`.
- **Events and edicts:** event namespace and ids are prefixed and consistent, every event title/desc/option and edict has
  localisation, every fired `lfg_` event exists, and every `lfg_` scripted trigger/effect (`x = yes`) and `value:lfg_` script value is defined.

CI (`.github/workflows/verify.yml`) runs the tests and the checks that don't need game files on every push.

**Still to test in game:**
- Each tree appears only for the right empires.
- The civic is blocked for cybernetic/machine/synthetic setups, and the two ascension perks show the new requirement.
- Hooks: scaled bonuses (per species, rival, contact, decade, stored food/energy) and tiers (megastructures, artificial worlds,
  robot share) apply as described; agendas appear after finishing their tree; Reckless Experimentation's lab accident fires.
- Species Experimentation: only Evolutionary Predators who finished Mutation see it; your main species and its subspecies are never offered;
  under 100 pops it's greyed out; picking a species kills half of it, creates 50 subspecies and deducts 2000 society research.
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
  `mod/descriptor.mod` first. Every upload also replaces the Steam description with `workshop_description.txt`
  (`SYNC_DESCRIPTION=0` to skip). `VISIBILITY=0|1|2|3` (public / friends-only / private / unlisted) updates visibility.
- `STEAM_USER` is your Steam **account name** (the login name, not your profile name). steamcmd asks for the password and
  Steam Guard code once, then caches the login. Nothing is stored in this repo.
- Double quotes in the description or change note are turned into “typographic quotes”, because steamcmd's VDF parser has no escapes.

Alternative: run `RELEASE=1 scripts/install.sh` (so the upload isn't named "[LOCAL DEV]"), then use the Paradox launcher's **Upload mod** and copy the `remote_file_id` it writes
into `mod/descriptor.mod`.

Publishing to the Workshop is local-only on purpose: CI would need your Steam credentials, and the strict checks need the game installed.

## Ideas for later

- **Leisure Society** (civilians over workers) was removed for a rework; the old version is in git history (before this change).

- Custom icons and art instead of reused vanilla icons.
- `tradition_swap` variants with gestalt- and nomad-specific names and text.
- Planet-level effects for Shellworlders that apply only on artificial worlds (needs scripted planet modifiers).
- A start-of-game effect for Pampered Masters that gives the founder robots *Domestic Protocols* and Servitude citizenship.
