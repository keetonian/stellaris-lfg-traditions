# LFG Traditions

A Stellaris **4.5** mod for **Gigastructural Engineering & More (4.5)** games that adds:

- **7 tradition trees**, each with a hook that scales with your game state, available only to fitting empires.
- **6 council agendas** unlocked by the trees (The Great Project has two versions, with and without supertensiles).
- **1 ascension perk, Curated Progress** (after Gigastructural Constructs): unlocks 27 **Shelve** edicts that stop specific repeatable techs from being offered as research options.
- **1 edict, Species Experimentation** (Evolutionary Predators, after finishing Mutation): half of a secondary species dies, the rest splits into 50 random-trait subspecies.
- **Overrides** of vanilla/Gigastructural definitions (generated, see [Overrides](#overrides-of-vanilla-and-gigastructural-content)): Synthetic Fertility's situation speeds up every year, two trees extend the Accommodation District and holomuseums, and the repeatable techs check the Shelve edicts.

This is a gameplay mod (it adds `common/` files), so it **changes the game checksum**. Everyone in a multiplayer game needs it.

> **Status: draft.** The balance numbers are a first pass and haven't been playtested. Everything is checked statically
> (see [Verification](#verification)), but in-game testing is still to do.

## Requirements

- Stellaris 4.5.x
- [Gigastructural Engineering & More (4.5)](https://steamcommunity.com/sharedfiles/filedetails/?id=1121692237). Required: the Megaforge tree uses its supertensiles, techs and origins.
- Recommended: [A Lot of Traditions - 24 Tradition Slots](https://steamcommunity.com/sharedfiles/filedetails/?id=3089158981).
  Vanilla allows 7 trees in total, and this mod adds 7 more options. Compatible with Expanded Stellaris Traditions and More Traditions (no shared keys).

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

### Shellworlders: life on artificial worlds
**Who:** artificial-world origins (Giga: Frameworld, Decaying Birch World, Great Ring, Interstellar Ring, Alderson Disk;
vanilla: Shattered Ring, Void Dwellers), or after *Orbital Habitats* / *Ring World*. **Hook:** every bonus applies on your
**artificial worlds** (`is_artificial`: habitats, ring segments, Alderson Disk slices, Maginot worlds and Giga's other habitable
megastructures), and megastructure build speed grows with how many you own.

| Tradition | Effect |
|---|---|
| Adopt | Artificial worlds: job efficiency +5% · habitat cost −10% · **organic growth −10%, robot assembly −10%** |
| 1. Compact Living | Artificial worlds: housing usage −10% |
| 2. Artificial Gravity | Artificial worlds: stability +3, crime −15 |
| 3. Arc Foundries ⚙ | Megastructure build speed +5% per artificial world owned (no cap) |
| 4. Closed Ecology | Artificial worlds: job efficiency +10% · **natural worlds: happiness −10%, stability −10%** |
| 5. Arc Neighbours ⚙ | Each artificial world: job efficiency +3% per other artificial world you own in its system (no cap; a full ring world gives each segment +9%) |
| Finish | +1 max districts on artificial worlds |

Tradition modifiers are empire-wide, so the planet effects are static modifiers (`lfg_shellworld_*`, one per tradition)
that the hidden event `lfg_shellworlders.1` keeps on every owned artificial world: on adoption and monthly (new or lost
worlds can lag up to a month). The natural-world penalty is `lfg_shellworld_natural_world`, kept the same way. Arc Neighbours
re-adds its modifier with the neighbour count as multiplier when the count changes (planet variable `lfg_arc_neighbours`).
When a planet changes owner, `lfg_planet.1` (`on_colony_transfer`/`on_colony_ownerless`) strips all these per-planet modifiers
(and Galactic Destination's); the new owner's sync re-adds its own. The finisher uses vanilla's `planet_artificial_max_districts_add`, which applies instantly.

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

### Evolutionary Perfection: every trait is an advantage
**Who:** any empire. **Hook:** scales with your main species' traits, your species and subspecies, and the planet types you live on (all uncapped).

| Tradition | Effect |
|---|---|
| Adopt | Species modification cost −25% |
| 1. Strength Through Hardship ⚙ | Per **negative** trait of the main species: organic pop growth +5%, pop assembly +5% |
| 2. Honed Strengths ⚙ | Per **positive** trait of the main species: job efficiency +1% |
| 3. Migratory Instinct ⚙ | Per species in the empire: ship speed +1% |
| 4. Branching Lineages ⚙ | Per subspecies of the main species: society research +2% |
| 5. Every Shore ⚙ | Per planet type you have a colony on: diplomatic weight +1% |
| Finish | +1 ascension perk slot · +1 species trait point and +1 trait pick (biological, lithoid, robot, machine) |

Traits are counted by the game's `num_negative_traits` / `num_positive_traits` (trait cost < 0 / > 0) on the country, i.e.
its main species. "Planet types" is `value:lfg_num_world_types`, generated by `tools/gen_overrides.py` from every
`colonizable = yes` planet class in vanilla and Gigastructural (~50).

### Granary Kings: the food stockpile is political power
**Who:** empires whose **main species eats food** (biological species, voidlings included; not lithoids, machines or robots). Hives get their own description. **Hook:** your food stockpile and income drive the bonuses.
**Agendas:** Feast of Plenty (on adoption), The Harvest Tithe (finisher).

| Tradition | Effect |
|---|---|
| Adopt | Storage +10,000 for every resource, farmer output +10% · unlocks agenda **Feast of Plenty** |
| 1. Tithe Barns ⚙ | 10,000+ food stored: stability +5, organic growth +10% · under 1,000: stability −5, organic growth −10% |
| 2. Seed Vaults ⚙ | Unity +1% per 5,000 stored food (max +20%) |
| 3. Bountiful Fields | Farmer output +20% |
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
**Who:** regular empires. **Adopt requires:** *Resort Colonies*. **Hook:** an empire can only have **one** resort world, so bonuses scale with how built-up it is: per 100 Resort Workers employed and per 1,000 Tourists there (both uncapped).
**Tourists** are vanilla's civilian job on a resort world (2 trade + 50 amenities each).
**Pleasure Worlds** (Shroud, Bliss Accord) are resort colonies with a different designation, so everything here applies to them too
(the mod only checks the `resort_colony` modifier, never the `col_resort` designation).
**Agenda (on adoption):** Grand Tour Season. Resort Workers share the entertainer category, so entertainer bonuses (e.g. Galactic Broadcast) also boost them.

| Tradition | Effect |
|---|---|
| Adopt | Resort Worker workforce +10%, resort district build speed +25% · unlocks agenda **Grand Tour Season** |
| 1. Hospitality Academies | Each **Accommodation District** gives +150 Resort Worker jobs (+50%; via a generated `district_resort` override), and every resort-world **district specialization** gives +50% jobs: Resort (+50 Resort Workers), Entertainment (+50 Entertainers), and the attractions Zoo (+100 Biologists), Grand Museum and Spiritual Retreat (+100 Bureaucrats), Hunting Ground (+100 Wranglers), Restoration Enclave (+100 Healthcare), Proving Grounds (+100 Entertainers). Generated zone overrides, modelled on vanilla's Commercial Enterprise |
| 2. Package Holidays ⚙ | Per 100 Resort Workers (no cap): unity +0.5%, pop happiness +0.25% |
| 3. Paradise Unbound | Each Accommodation District adds +0.5 max districts to the resort world · unlocks the **Expand the Resort** decision · +1 max Accommodation District, resort district build speed +25% |
| 4. Tourist Traps | Resort Worker workforce +15% · entertainer/resort worker consumer goods upkeep +0.5 |
| 5. Galactic Destination ⚙ | On the resort world: **Tourists** +1 trade and +1 unity, unemployed pops +50% more likely to move there · diplomatic weight +1% per 1,000 Tourists there (no cap). The planet part is the `lfg_galactic_destination` modifier, kept on the resort world by the monthly hidden event `lfg_resorts.1`, which also stores the tourist count (`num_assigned_jobs = { job = civilian }`) in `lfg_tourists`; so it can lag up to a month |
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
| Eureka Season | Polymath | Research speed +3% | Research speed +20% · stability −5 |
| Feast of Plenty | Granary (on adoption) | Farmer output +5% | For 10 years: doubles the finisher's Bumper Crops (another +1% organic growth per 1,000 monthly food income) |
| The Harvest Tithe | Granary | Farmer output +5% | On launch, if you have 3,000 food: −3,000 food, +150 influence, +2,000 unity. Then food +10%, stability +2 |
| Gala Season | Galactic Broadcast | Entertainer output +5% | Happiness +10%, unity +10% · trade −10% |
| Grand Tour Season | The Grand Tour (on adoption) | Resort Worker workforce +5% | Happiness +10%, trade +15%, Resort Worker workforce +25% · worker output −5% |

## Special system: Lone Tide

In **75%** of games, a hidden `on_game_start` event (`lfg_lone_tide.1`) spawns **Lone Tide**: a G-type system just beyond
the galactic rim (about 40 units past the edge for every galaxy size, away from the L-Cluster) with **no hyperlanes**,
so it can only be reached by jump drives and similar. Its size **35 ocean world, Thalassa**, is home to a pre-FTL
civilization generated by vanilla's `generate_pre_ftls_on_planet` (random species, age and population).
It also has a molten world, a ringed gas giant and a frozen world. Initializer: `common/solar_system_initializers/lfg_system_initializers.txt`.

## Ascension perk: Curated Progress

Not every repeatable is worth chasing. **Curated Progress** (`ap_lfg_curated_progress`) unlocks one perpetual
**Shelve** edict per repeatable tech; while an edict is active, that tech is never drawn as a research option.

- **Requires:** the Gigastructural **Gigastructural Constructs** ascension perk (via Giga's `has_gigastructural_constructs`
  trigger). Hidden if Giga's perk is disabled by game rule. The AI never takes it and never enacts the edicts.
- **Each edict costs** 2,000 unity + 200 influence to enact and **300 monthly research of the shelved tech's type**
  (engineering/physics/society) while active. All of it scales with empire size like vanilla edicts
  (`value:edict_size_effect`: +1% per point of empire size over capacity). Numbers: `@lfg_shelve_*` in
  `mod/common/scripted_variables/lfg_scripted_variables.txt`.
- **How it works:** each repeatable's `weight_modifier` gets `modifier = { factor = 0 has_edict = <edict> }` (generated
  tech overrides). A tech already in your current research options stays there until you pick another option.
- **Edicts only show up once the tech can:** each edict's `potential` also needs the tech's prerequisite (or Giga's flag/origin
  for special repeatables), and an active edict always stays visible.
- Gigastructural's ~50 **megastructure capacity** repeatables (+1 cap per megastructure type) share one inline script, so they get
  one edict per research area.
- The edicts and their localisation are **generated** from the `SHELVE` table in `tools/gen_overrides.py`
  (`lfg_shelve_edicts.txt`, `lfg_shelve_l_english.yml`); names use the tech's own name ("Shelve: Extraction Patterns"), and each description ends with what one level of the
  tech gives (`SHELVE_EFFECTS`; the generator fails if a tech's value changes, so the text can't go stale).

| Edict | Tech | Research upkeep | Shown once you have |
|---|---|---|---|
| `lfg_shelve_mineral_output` | `tech_repeatable_improved_tile_mineral_output` (vanilla) | Engineering | `has_technology = tech_mineral_purification_2` |
| `lfg_shelve_station_damage` | `tech_repeatable_improved_military_station_damage` (vanilla) | Engineering | `has_technology = tech_defense_platform_hull_1` |
| `lfg_shelve_station_health` | `tech_repeatable_improved_military_station_health` (vanilla) | Engineering | `has_technology = tech_defense_platform_hull_1` |
| `lfg_shelve_armor` | `tech_repeatable_improved_armor_output` (vanilla) | Engineering | `has_technology = tech_ship_armor_3` |
| `lfg_shelve_explosive_damage` | `tech_repeatable_weapon_type_explosive_damage` (vanilla) | Engineering | `tech_missiles_3` or `tech_swarmer_missiles_2` |
| `lfg_shelve_explosive_fire_rate` | `tech_repeatable_weapon_type_explosive_fire_rate` (vanilla) | Engineering | `tech_missiles_3` or `tech_swarmer_missiles_2` |
| `lfg_shelve_kinetic_damage` | `tech_repeatable_weapon_type_kinetic_damage` (vanilla) | Engineering | `has_technology = tech_mass_drivers_3` |
| `lfg_shelve_kinetic_fire_rate` | `tech_repeatable_weapon_type_kinetic_fire_rate` (vanilla) | Engineering | `has_technology = tech_mass_drivers_3` |
| `lfg_shelve_blokkat_scrap_damage` | `giga_tech_blokkat_scrap_damage` (Giga) | Engineering | `has_country_flag = researching_blokkat_scrap_damage` |
| `lfg_shelve_energy_output` | `tech_repeatable_improved_tile_energy_output` (vanilla) | Physics | `has_technology = tech_power_plant_3` |
| `lfg_shelve_shields` | `tech_repeatable_improved_shield_output` (vanilla) | Physics | `has_technology = tech_shields_4` |
| `lfg_shelve_energy_damage` | `tech_repeatable_weapon_type_energy_damage` (vanilla) | Physics | `has_technology = tech_lasers_4` |
| `lfg_shelve_energy_fire_rate` | `tech_repeatable_weapon_type_energy_fire_rate` (vanilla) | Physics | `has_technology = tech_lasers_2` |
| `lfg_shelve_dimensional_storage` | `giga_tech_repeatable_dimensional_storage` (Giga) | Physics | `has_technology = giga_tech_tetradimensional_engineering` |
| `lfg_shelve_food_output` | `tech_repeatable_improved_tile_food_output` (vanilla) | Society | `has_technology = tech_gene_crops` |
| `lfg_shelve_core_system_cap` | `tech_repeatable_improved_core_system_cap` (vanilla) | Society | `has_technology = tech_galactic_bureaucracy` |
| `lfg_shelve_army_damage` | `tech_repeatable_improved_army_damage` (vanilla) | Society | `has_technology = tech_combat_training` |
| `lfg_shelve_army_health` | `tech_repeatable_improved_army_health` (vanilla) | Society | `has_technology = tech_combat_training` |
| `lfg_shelve_leader_life_span` | `tech_repeatable_improved_leader_life_span` (vanilla) | Society | `has_technology = tech_vitality_boosters` |
| `lfg_shelve_strike_craft_damage` | `tech_repeatable_weapon_type_strike_craft_fire_damage` (vanilla) | Society | `has_technology = tech_strike_craft_3` |
| `lfg_shelve_strike_craft_fire_rate` | `tech_repeatable_weapon_type_strike_craft_fire_rate` (vanilla) | Society | `has_technology = tech_strike_craft_3` |
| `lfg_shelve_blokkat_scrap_research` | `giga_tech_blokkat_scrap_research` (Giga) | Society | `has_country_flag = researching_blokkat_scrap_research` |
| `lfg_shelve_frameworld_outposts` | `tech_frameworld_repeatable_outpost_output` (Giga) | Society | `giga_has_frameworld_origin = yes` |
| `lfg_shelve_eawaf_weapons` | `giga_tech_eawaf_weapons_repeatable` (Giga) | Society | `has_country_flag = giga_tech_eawaf_weapons_repeatable_possible` |
| `lfg_shelve_megastructure_capacity_engineering` | every Giga `giga_tech_repeatable_*_cap` in engineering | Engineering | always |
| `lfg_shelve_megastructure_capacity_physics` | every Giga `giga_tech_repeatable_*_cap` in physics | Physics | always |
| `lfg_shelve_megastructure_capacity_society` | every Giga `giga_tech_repeatable_*_cap` in society | Society | always |

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

## Overrides of vanilla and Gigastructural content

These replace vanilla and Gigastructural definitions. Other mods that change the same definitions will conflict; whichever loads last wins.

| Vanilla definition | Change |
|---|---|
| Buildings `xeno_geology_holomuseum`, `aesthetic_wonders_holomuseum`, `galactic_history_holomuseum` | Added: their entertainer unity/research bonus again while the owner has Holo-Museums |
| District `district_resort` (Accommodation District) | Added: +150 Resort Worker jobs per district (Hospitality Academies) and +0.5 max districts per district (Paradise Unbound) |
| The 24 repeatable techs in the Curated Progress table (19 vanilla, 5 Giga) | Added to `weight_modifier`: never drawn while their Shelve edict is active |
| Giga inline script `common/inline_scripts/technology/giga_mega_repeatable.txt` (all megastructure capacity repeatables) | Same, with `has_edict = lfg_shelve_megastructure_capacity_$area$`. Inline scripts can only be replaced as a whole file (same path, this mod loads after Giga) |
| Event `machine_age.4400` (Synthetic Age transformation: pick Nanotech / Modularity / Virtuality) | Virtuality option greyed out ("Individual machine empires whose origin is The Great Ring or Alderson Disk cannot take the Virtuality path") for **individual machine** empires with Giga's **The Great Ring** or **Alderson Disk** origin. Machine Intelligences and other origins are unaffected. Events are first-definition-wins, so this file is `events/00_lfg_event_overrides.txt` (sorts before vanilla's) |
| The 8 resort-world zones (`zone_resort`, `zone_resort_entertainment`, `zone_resort_zoo`, `zone_resort_grand_museum`, `zone_resort_hunting_ground`, `zone_resort_spiritual_retreat`, `zone_resort_restoration_enclave`, `zone_resort_proving_grounds`) | Added: +50% of the zone's jobs with Hospitality Academies |
| Giga loc `origin_tooltip_great_ring_effects`, `origin_alderson_effects` (origin selection cards) | Appended: "Individual machine empires can't take the Virtuality path (LFG Traditions)." Generated from Giga's text into `localisation/english/replace/` |
| Situation `situation_synthetic_fertility_digitization` (the Synthetic Fertility origin's "uploading" situation) | Monthly progress **+1 for every year since game start**, on top of the vanilla base of 15 (year 10: 25/month). It completes noticeably sooner. |

The override files are **generated** from the installed game and Gigastructural by `tools/gen_overrides.py`, so they're
their text plus clearly marked `# LFG: added` lines. The tech overrides are named `zz_lfg_` so they load after Giga's `zz_giga_` files.

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
scripts/verify.sh                    # 84 tests + static check
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
- **Overrides:** the override files, Shelve edicts and their loc match a fresh `tools/gen_overrides.py` run; every
  `has_edict = lfg_*` (including `$area$` in the inline script) names an edict in this mod; `$key$` references in the loc exist.
- **Ascension perks:** loc (`key`, `_desc`), a `GFX_<perk>` sprite, and every `has_ascension_perk` exists.
- **Modifier names:** every job/district-generated modifier shown in a tooltip has a name in the game, Giga or `lfg_modifiers_l_english.yml`
  (otherwise the tooltip shows the raw `mod_...` key), unless it's hidden behind `show_only_custom_tooltip`.
- **Events and edicts:** event namespace and ids are prefixed and consistent, every event title/desc/option and edict has
  localisation, every fired `lfg_` event exists, and every `lfg_` scripted trigger/effect (`x = yes`) and `value:lfg_` script value is defined.

CI (`.github/workflows/verify.yml`) runs the tests and the checks that don't need game files on every push.

**Verified in game:**
- Expand the Resort: the decision works, including its growing cost and the expansion modifier applied with
  `multiplier = <planet variable>`.

**Still to test in game:**
- Lone Tide: spawns in ~3 of 4 games beyond the rim with no hyperlanes; Thalassa (size 35 ocean) has a pre-FTL civilization.
- Evolutionary Perfection: trait counts, subspecies count and planet-type count drive the bonuses.
- Shellworlders: modifiers appear on artificial / natural worlds; Arc Neighbours scales with neighbours in the system.
- Virtuality block: an individual machine Great Ring / Alderson Disk empire sees Virtuality greyed out in the Synthetic Age path choice
  (and error.log shows our `machine_age.4400` winning, not vanilla's).
- Curated Progress: shown after Gigastructural Constructs; Shelve edicts appear with the tech's name, charge research upkeep,
  and a shelved tech (including a megastructure capacity repeatable) stops appearing in new research options.
- Each tree appears only for the right empires.
- Hooks: scaled bonuses (per species, rival, contact, megastructure, artificial world, stored food, food income,
  Resort Worker, Tourist) apply as described; agendas appear after finishing their tree; Reckless Experimentation's lab accident fires.
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

- Rework **Overclocked Network** (Machine Intelligence: complex vs simple drones; removed in 0.2.1, last version in git history).

- **Leisure Society** (civilians over workers) was removed for a rework; the old version is in git history (before this change).

- Custom icons and art instead of reused vanilla icons.
- `tradition_swap` variants with gestalt- and nomad-specific names and text.
