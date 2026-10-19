# LFG Traditions

A Stellaris **4.5** mod for **Gigastructural Engineering & More (4.5)** games that adds:

- **8 tradition trees**, each with a hook that scales with your game state, available only to fitting empires.
- **6 council agendas** unlocked by the trees (The Great Project has two versions, with and without supertensiles).
- **2 ascension perks:** **Curated Progress** (after Gigastructural Constructs) unlocks 27 **Shelve** edicts that stop specific repeatable techs from being offered as research options; **Massed Assault** gives +10 ground combat width and a general trait that boosts the armies they lead.
- **1 civic, Applied Biosciences** (materialist, non-machine species): Biologists research less society but some physics and engineering.
- **1 edict, Species Experimentation** (Evolutionary Predators, after finishing Mutation): half of a secondary species dies, the rest splits into 50 subspecies, each with a random positive and a random negative trait.
- **Overrides** of vanilla/Gigastructural definitions (generated, see [Overrides](#overrides-of-vanilla-and-gigastructural-content)): Synthetic Fertility's situation speeds up every year, three trees extend the Accommodation District, holomuseums and the Archaeostudies Faculty, and the repeatable techs check the Shelve edicts.

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

### Megaforge: megastructures over the normal economy
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
| 5. Monument Economy ⚙ | Unlocks the **Monument Economy** policy. Per megastructure owned (kilostructures count, ruins don't): *Balanced* (default) no effect, *Monuments First* megastructure output +1% · job output −0.5%, or *People First* job output +0.5% · megastructure output −1%. Monthly supertensiles +10 |
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
| 3. Arc Foundries ⚙ | Megastructure build speed +5% per artificial world owned |
| 4. Closed Ecology | Artificial worlds: job efficiency +10% · **natural worlds: happiness −10%, stability −10%** |
| 5. Arc Neighbours ⚙ | Each artificial world: job efficiency +3% per other artificial world you own in its system (a full ring world gives each segment +9%) |
| Finish | +1 max districts on artificial worlds |

Tradition modifiers are empire-wide, so the planet effects are static modifiers (`lfg_shellworld_*`, one per tradition)
that the hidden event `lfg_shellworlders.1` keeps on every owned artificial world: on adoption and monthly (new or lost
worlds can lag up to a month). The natural-world penalty is `lfg_shellworld_natural_world`, kept the same way. Arc Neighbours
re-adds its modifier with the neighbour count as multiplier when the count changes (planet variable `lfg_arc_neighbours`).
When a planet changes owner, `lfg_planet.1` (`on_colony_transfer`/`on_colony_ownerless`) strips all these per-planet modifiers
(and Galactic Destination's); the new owner's sync re-adds its own. The finisher uses vanilla's `planet_artificial_max_districts_add`, which applies instantly.

### Xenoarchaeology: scientists hunt anomalies and relics
**Who:** empires with the Ancient Relics DLC (minor artifacts and relics). **Hook:** research grows with every anomaly studied and every relic owned (uncapped); minor artifacts buy new dig sites, anomalies and astral rifts. **Agenda:** Grand Expedition.
Vanilla Archivism already covers specimens, so this tree doesn't.

| Tradition | Effect |
|---|---|
| Adopt | Anomaly discovery chance +10% · scientist upkeep +10% · starts counting anomalies for Anomaly Studies |
| 1. Field Expeditions | Survey speed +25% · anomaly research speed +15% |
| 2. Anomaly Studies ⚙ | Research speed +0.25% per anomaly researched since adopting the tree (uncapped) · every anomaly researched gives +5 minor artifacts |
| 3. Reverse Engineering ⚙ | Archaeotech weapon damage +10% · research speed +5% per relic owned (uncapped) |
| 4. Expedition Corps | Scientist cap +1 · scientist experience gain +15% · **Archaeo-Engineer** output +25% (Biologists on a planet with an Archaeostudies Faculty; generated `building_archaeostudies_faculty` override) |
| 5. Commissioned Digs | Unlocks the minor artifact action **Commission a Dig** (2,000 minor artifacts): a popup lets you choose a new **archaeological site**, **anomaly** or (with Astral Planes) **astral rift** within your borders |
| Finish | Anomaly discovery chance +15% · unlocks agenda **Grand Expedition** |

Anomalies are counted by the hidden ship event `lfg_xenoarchaeology.1`, fired from vanilla's `anomaly_success` on_action: it increments the country variable `lfg_anomalies_studied` (read by `value:lfg_anomalies_studied`) and, with Anomaly Studies, adds the minor artifacts.
Relics are counted with `num_owned_relics` (`value:lfg_num_relics`).

**Commission a Dig** (`artifact_lfg_commission_dig`, `common/artifact_actions/`) charges the minor artifacts and opens the popup
`lfg_xenoarchaeology.2`. Each option is greyed out when impossible, and "Not now" refunds the cost:
- **Dig Site:** `create_archaeological_site = random` on a planet within your borders that passes `can_spawn_random_archaeological_site`.
- **Anomaly:** `spawn_random_anomaly` on an uncolonized planet within your borders without one, with any of your science ships as the
  surveyor (the effect requires one; vanilla's deep scan does the same).
- **Astral Rift:** only shown with Astral Planes; `spawn_astral_rift` in a system that passes vanilla's `can_spawn_astral_rift`
  (no rift or scar in or next to it), like vanilla's Astral Splitting.

`lfg_xenoarchaeology.3` then says where it is. If no spot fits after all, the cost is refunded.
**Unverified in game:** that `spawn_random_anomaly` works on already-surveyed planets, and the option `allow` tooltips.

### Lineage: every trait is an advantage
**Who:** any empire. **Hook:** scales with your main species' traits, your species and subspecies, and the planet types you live on (all uncapped).

| Tradition | Effect |
|---|---|
| Adopt | Species modification cost −25% |
| 1. Strength Through Hardship ⚙ | Per **negative** trait of the main species: organic pop growth +5%, pop assembly +5% |
| 2. Honed Strengths ⚙ | Per **positive** trait of the main species: job efficiency +1% |
| 3. Migratory Instinct ⚙ | Per species in the empire: ship speed +1% |
| 4. Branching Lineages ⚙ | Per subspecies of the main species: society research +2% |
| 5. Every Shore ⚙ | Per planet type you have a colony on: diplomatic weight +1% |
| Finish | +1 ascension perk slot · +1 species trait point and +1 trait pick (biological, lithoid, robot, machine; one tooltip line via the static modifier `lfg_lineage_finish`) |

Traits are counted by the game's `num_negative_traits` / `num_positive_traits` (trait cost < 0 / > 0) on the country, i.e.
its main species. "Planet types" is `value:lfg_num_world_types`, generated by `tools/gen_overrides.py` from every
`colonizable = yes` planet class in vanilla and Gigastructural (~50).

### Penitence: the penal colony runs the economy
**Who:** regular empires (like penal colonies). **Adopt requires:** *Penal Colonies*. **Hook:** an empire has only one
penal colony, so the tree scales with it: per 100 unemployed pops there and per Prison District there (uncapped).

Layout (like vanilla Statecraft): Wardens' Code → Transportation → Idle Hands, and Prison Industry → Chain Gangs.

"Unemployed" here means **Civilians**: in 4.5 a regular empire's jobless pops take the uncapped Civilian job, so the
tree counts `num_assigned_jobs = { job = civilian }` (vanilla's `num_unemployed` is always 0 for regular empires).

| Tradition | Effect |
|---|---|
| Adopt | Penal colony: worker job efficiency +10%, housing +25% · **worker happiness −5% everywhere** |
| 1. Wardens' Code | Penal colony: stability +5, enforcer job efficiency +20% |
| 2. Transportation | Crime −10% everywhere · **every month, 10% of the unemployed on each other planet (max 300 per planet) are shipped to the penal colony**, jobs and housing or not (`lfg_penal_ship_unemployed` in `lfg_penal.1`; vanilla resettlement only targets planets with open jobs) |
| 3. Idle Hands ⚙ | **All jobs on the penal colony +1% per 100 unemployed pops there** · **with fewer than 100 unemployed: −75% job output there instead** · **riots:** crime +2 per 100 unemployed · **attrition:** 3% of the unemployed there die each month, so they settle at ~33× monthly arrivals (+33% per 100 arrivals/month; ~31% lost per year) |
| 4. Prison Industry ⚙ | **+50% jobs from district specializations on the penal colony** (generated additions to the 12 city specializations: Industrial, Foundry, Factory, the research and unity ones, Fortress, Trade; and the Penal Supertensile Works) |
| 5. Chain Gangs | Penal colony: worker job efficiency +15%, pop upkeep −15%, **happiness −15%** |
| Finish | Unlocks the penal specializations for Prison Districts on the penal colony: with supertensiles on, the **Penal Supertensile Works** specialization in Prison Districts there (+100 **Penal Supertensile Laborer** jobs: 4 minerals + 1 alloy + 1 unity → 1 supertensile each) · with Gigastructural's bulk matter enabled: the **Penal Matter Compactors** specialization (+100 **Penal Matter Compactor** jobs: 180 energy + 30 minerals + 40 alloys + 0.5 dark matter → 0.01 bulk matter each per month, i.e. 18,000 energy + 3,000 minerals + 4,000 alloys + 50 dark matter per matter; Giga's harvesting costs 16,000 energy + 4,000 alloys) · **Expand the Cell Blocks** decision on the penal colony: +1,500 housing per use, up to 10 times; costs (400 minerals + 200 alloys) × (uses + 1) + 25 influence, 180 days |

Planet effects are `lfg_penal_*` modifiers kept on the penal colony by the
monthly hidden event `lfg_penal.1` (also run on adoption), which counts its Prison Districts
(Prison Industry's modifier is re-added with that count as multiplier) and its unemployed pops (`lfg_penal_idle_hands`,
multiplier = whole hundreds of unemployed). Changes can lag up to a month. The Penal Supertensile Works zone
(`common/zones/lfg_zones.txt`) and its job (`common/pop_jobs/lfg_jobs.txt`, own economic category `planet_lfg_penal_laborers`)
are new content, modelled on vanilla's Heavy Industry zone and Gigastructural's Supertensiles Extractor.

### Abundance: the food stockpile is political power
**Who:** empires whose **main species eats food** (biological species, voidlings included; not lithoids, machines or robots). Hives get their own description. **Hook:** your food stockpile and income drive the bonuses.
**Agendas:** Feast of Plenty (on adoption), The Harvest Tithe (finisher).

| Tradition | Effect |
|---|---|
| Adopt | Storage +10,000 for every resource, farmer output +10% · unlocks agenda **Feast of Plenty** |
| 1. Tithe Barns ⚙ | 10,000+ food stored: stability +5, organic growth +10% · under 1,000: stability −5, organic growth −10% |
| 2. Seed Vaults ⚙ | Unity +1% per 5,000 stored food (max +20%) |
| 3. Bountiful Fields | Farmer output +20% |
| 4. Grain Reserves | Food storage +100,000 · pop food upkeep +200% |
| 5. Harvest Courts ⚙ | Worker political power +25% · specialist political power −25% · while food income is positive: influence +10% |
| Finish ⚙ | **Bumper Crops:** organic growth +1% per 1,000 food produced per month (the food tooltip's "Produced" line: trade deals and upkeep don't count; doubled during **Feast of Plenty**) · unlocks agenda **The Harvest Tithe** |

### Broadcast: entertainment for the whole galaxy
**Who:** non-gestalt (gestalts have no entertainers). **Hook:** scales with the empires you know and your commercial pacts; war is prime time; doubles your holomuseums. **Agenda:** Gala Season.

| Tradition | Effect |
|---|---|
| Adopt ⚙ | Trade +1% per empire in contact (max +20%), entertainer output +5% |
| 1. Holo-Museums | Every Grand Archive holomuseum you own grants its base bonuses again (stacks with other sources): specimen bonus +15% more, and its planet's entertainers get its +0.25 unity and +0.25 research again (generated building override) |
| 2. Celebrity Council | Council agenda speed +15%, entertainer unity +0.25 |
| 3. Propaganda Serials | Diplomatic weight +10% · government ethic attraction −15% |
| 4. Ratings War ⚙ | Envoys harming relations +50% · while at war: war exhaustion gain −20%, entertainer output +20% |
| 5. Syndication Deals ⚙ | Per commercial pact: entertainers +0.5 trade per 100 entertainers · +1 envoy, envoys improving relations +25% · researcher output −5% |
| Finish ⚙ | **Star Power:** diplomatic weight +1% per 1,000 entertainers employed (max +30%; `value:lfg_entertainer_thousands`) · unlocks agenda **Gala Season** |

### Tourism: resort worlds as showpieces
**Who:** regular empires. **Adopt requires:** *Resort Colonies*. **Hook:** an empire can only have **one** resort world, so bonuses scale with how built-up it is: per 100 Resort Workers employed and per 1,000 Tourists there (diplomatic weight capped at +30%).
**Tourists** are vanilla's civilian job on a resort world (2 trade + 50 amenities each).
**Pleasure Worlds** (Shroud, Bliss Accord) are resort colonies with a different designation, so everything here applies to them too
(the mod only checks the `resort_colony` modifier, never the `col_resort` designation).
**Agenda (on adoption):** Grand Tour Season. Resort Workers share the entertainer category, so entertainer bonuses (e.g. Broadcast) also boost them.

| Tradition | Effect |
|---|---|
| Adopt | Resort Worker workforce +10%, resort district build speed +25% · unlocks agenda **Grand Tour Season** |
| 1. Hospitality Academies | Each **Accommodation District** gives +150 Resort Worker jobs (+50%; via a generated `district_resort` override), and every resort-world **district specialization** gives +50% jobs: Resort (+50 Resort Workers), Entertainment (+50 Entertainers), and the attractions Zoo (+100 Biologists), Grand Museum and Spiritual Retreat (+100 Bureaucrats), Hunting Ground (+100 Wranglers), Restoration Enclave (+100 Healthcare), Proving Grounds (+100 Entertainers). Generated zone overrides, modelled on vanilla's Commercial Enterprise |
| 2. Package Holidays ⚙ | Per 100 Resort Workers: unity +0.5%, pop happiness +0.25% |
| 3. Paradise Unbound | Each Accommodation District adds +0.5 max districts to the resort world · unlocks the **Expand the Resort** decision · +1 max Accommodation District, resort district build speed +25% |
| 4. Tourist Traps | Resort Worker workforce +15% · entertainer/resort worker consumer goods upkeep +0.5 |
| 5. Galactic Destination ⚙ | On the resort world: **Tourists** +0.5 trade · diplomatic weight +1% per 1,000 Tourists there (max +30%). The planet part is the `lfg_galactic_destination` modifier, kept on the resort world by the monthly hidden event `lfg_resorts.1`, which also stores the tourist count (`num_assigned_jobs = { job = civilian }`) in `lfg_tourists`; so it can lag up to a month |
| Finish | Resort world: job efficiency +10% (planet modifier `lfg_tourism_finish`, kept by `lfg_resorts.1`) |

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
| Grand Expedition | Xenoarchaeology | Anomaly research speed +10% · research speed −5% | Anomaly research, survey and excavation speed +50% · research speed −10% |
| Feast of Plenty | Granary (on adoption) | Farmer output +5% | For 10 years: doubles the finisher's Bumper Crops (another +1% organic growth per 1,000 food produced per month) |
| The Harvest Tithe | Granary | Farmer output +5% | On launch, if you have 3,000 food: −3,000 food, +150 influence, +2,000 unity. Then food +10%, stability +2 |
| Gala Season | Broadcast | Entertainer output +5% | Happiness +10%, unity +10% · trade −10% |
| Grand Tour Season | Tourism (on adoption) | Resort Worker workforce +5% | Happiness +10%, trade +15%, Resort Worker workforce +25% · worker output −5% |

## Special system: Lone Tide (secret: not on the Steam page)

In **75%** of games, a hidden `on_game_start` event (`lfg_lone_tide.1`) spawns **Lone Tide**: a trinary system just beyond
the galactic rim (about 40 units past the edge for every galaxy size, away from the L-Cluster) with **no hyperlanes**,
so it can only be reached by jump drives and similar. Its size **35 ocean world, Thalassa**, is home to a pre-FTL
civilization generated by vanilla's `generate_pre_ftls_on_planet` (random species, age and population).
It's a **trinary** (blue B, white A and yellow-white F stars, vanilla `sc_trinary_2`, spread 120° apart on a ring around
an empty centre like the L-Cluster's) with **16 planets and 17 moons**: molten, toxic (1 moon),
Thalassa (2 moons), arid (1), a ringed gas giant (3), a second gas giant (2), a cold barren world, a frozen world (1),
an icy asteroid, tundra (1), a big ringed gas giant (4), toxic, a ringed frozen world (2), cold barren, and two more icy
asteroids, plus a rocky asteroid belt. Initializer: `common/solar_system_initializers/lfg_system_initializers.txt`.

## Special system: Emberfall (not on the Steam page)

In **every** game, a hidden `on_game_start` event (`lfg_emberfall.1`) spawns **Emberfall** 20–50 units from a random
system (not in an empire's or Fallen Empire's starting cluster), connected by hyperlanes like vanilla's Sealed System.
It has a single blue **B-class** star and one planet: **Crucible**, a **size 60 molten world** (vanilla's largest
gas giants are size 62; one base district per size). Initializer: `lfg_emberfall_init`.

## Civic: Applied Biosciences

**Who:** Materialist or Fanatic Materialist empires whose species isn't a machine (gestalts can't be materialist).
**Effect:** per Biologist job: society research **−1** (3 → 2), physics **+0.4**, engineering **+0.4** (vanilla's
`planet_biologists_*_research_produces_add`, so Biologist bonuses and job efficiency apply to all of it). The Biologist job's
variants (Rangers, Xeno-Zoo Keepers, Stratovent Researchers, Archaeo-Engineers) count too. Icon: vanilla Genetic Identification
recoloured to the mod's amber civic colour (`art/make_civic_icons.py`; every civic from this mod uses it).
**Council position:** **Chief Bioengineer** (scientists only; `councilor_lfg_applied_biosciences`): Biologist job efficiency
**+3% per level**. Not more physics per Biologist, because vanilla's Technocracy councilor (also Materialist) already gives that.

## Ascension perk: Massed Assault

**+10 ground combat width**: more armies fight at the same time. **Every general** also gets the **Massed Assault Doctrine**
trait (`leader_trait_lfg_massed_assault`; given on taking the perk and to every new leader via `on_leader_spawned` →
`lfg_massed_assault.1`): armies they lead get damage **+25%**, health **+25%**, morale **+50%** (`@lfg_massed_assault_general_*`). Base width is 5 + 0.2 × planet size (size 10: 7,
size 20: 9, size 25: 10), so this roughly doubles it; the only vanilla source is general traits (+1, +2, Paragon +10).
Requires **4 other ascension perks** first. The AI never takes it. Amount: `@lfg_massed_assault_width`.
**Unverified in game:** vanilla only uses `planet_combat_width_add` on generals, so check that the perk's country-wide
modifier reaches your invasions (the width shown in ground combat).

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
**50 subspecies**, each with **one extra random positive and one extra random negative organic trait**, with the population divided evenly between them.

- **Who:** empires with the **Evolutionary Predators** origin that have **finished the vanilla Mutation tradition tree**.
  The edict is hidden until then.
- **Requires:** a species that is **not your main species or any of its subspecies**, with at least **100 pops** (raw population, not 100-pop units).
  Greyed out until one qualifies.
- **Cost:** **1000 unity** to activate.
- **How it works:** activating the edict opens a popup listing up to 4 eligible species ("Show other species" re-rolls).
  Picking one kills 50% of every pop group of that species, then divides the rest 1/50, 1/49, … 1/1 so the shares come
  out equal. Small pop groups round, so some subspecies may end up with fewer pops.
- **Traits:** one positive and one negative, both organic and not special/cybernetic/presapient/drawback/genetic-ascension (like the origin's own mutations).
  The negative trait is added by a second `modify_species` on the new variant, so each subspecies leaves behind an empty intermediate species.
  Opposite traits (e.g. Strong + Weak) aren't filtered out.
- Numbers (50 subspecies, 100 pops) are in `mod/common/scripted_variables/lfg_scripted_variables.txt`.

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
| Buildings `xeno_geology_holomuseum`, `aesthetic_wonders_holomuseum`, `galactic_history_holomuseum` | Added: their specimen bonus and entertainer unity/research bonus again while the owner has Holo-Museums |
| Building `building_archaeostudies_faculty` | Added: Biologist (Archaeo-Engineer) output +25% on its planet while the owner has Expedition Corps |
| District `district_resort` (Accommodation District) | Added: +150 Resort Worker jobs per district (Hospitality Academies) and +0.5 max districts per district (Paradise Unbound) |
| The 24 repeatable techs in the Curated Progress table (19 vanilla, 5 Giga) | Added to `weight_modifier`: never drawn while their Shelve edict is active |
| Giga inline script `common/inline_scripts/technology/giga_mega_repeatable.txt` (all megastructure capacity repeatables) | Same, with `has_edict = lfg_shelve_megastructure_capacity_$area$`. Inline scripts can only be replaced as a whole file (same path, this mod loads after Giga) |
| Event `machine_age.4400` (Synthetic Age transformation: pick Nanotech / Modularity / Virtuality) | Virtuality option greyed out ("Individual machine empires whose origin is The Great Ring or Alderson Disk cannot take the Virtuality path") for **individual machine** empires with Giga's **The Great Ring** or **Alderson Disk** origin. Machine Intelligences and other origins are unaffected. Events are first-definition-wins, so this file is `events/00_lfg_event_overrides.txt` (sorts before vanilla's) |
| The 8 resort-world zones (`zone_resort`, `zone_resort_entertainment`, `zone_resort_zoo`, `zone_resort_grand_museum`, `zone_resort_hunting_ground`, `zone_resort_spiritual_retreat`, `zone_resort_restoration_enclave`, `zone_resort_proving_grounds`) | Added: +50% of the zone's jobs with Hospitality Academies |
| Giga loc `origin_tooltip_great_ring_effects`, `origin_alderson_effects` (origin selection cards) | Appended: "Individual machine empires can't take the Virtuality path (LFG Traditions)." Generated from Giga's text into `localisation/english/replace/` |
| Situation `situation_synthetic_fertility_digitization` (the Synthetic Fertility origin's "uploading" situation) | Monthly progress **+1 for every year since game start**, on top of the vanilla base of 15 (year 10: 25/month). It completes noticeably sooner. Each month, `lfg_synthetic_fertility.1` (added to the situation's `on_monthly` after vanilla's `machine_age.3325`) also uploads the **same number of extra pops** to the Identity Repository, the way vanilla does (one infected pop dies, its identity is stored), until none are left. |

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
- Synthetic Fertility: faster situation progress, and the extra monthly Identity Repository uploads (`lfg_synthetic_fertility.1`).
- Expand the Resort: the decision works, including its growing cost and the expansion modifier applied with
  `multiplier = <planet variable>`.

**Still to test in game:**
- Penitence: penal colony modifiers appear; Prison Industry jobs scale with Prison Districts;
  Penal Supertensile Works shows up in Prison Districts (supertensiles on); Idle Hands = +1% job output per 100 unemployed.
- Lone Tide: spawns in ~3 of 4 games beyond the rim with no hyperlanes; Thalassa (size 35 ocean) has a pre-FTL civilization.
- Lineage: trait counts, subspecies count and planet-type count drive the bonuses.
- Shellworlders: modifiers appear on artificial / natural worlds; Arc Neighbours scales with neighbours in the system.
- Virtuality block: an individual machine Great Ring / Alderson Disk empire sees Virtuality greyed out in the Synthetic Age path choice
  (and error.log shows our `machine_age.4400` winning, not vanilla's).
- Massed Assault: ground combat width +10 on your invasions; existing and new generals get Massed Assault Doctrine and
  their armies show the bonuses.
- Curated Progress: shown after Gigastructural Constructs; Shelve edicts appear with the tech's name, charge research upkeep,
  and a shelved tech (including a megastructure capacity repeatable) stops appearing in new research options.
- Each tree appears only for the right empires.
- Hooks: scaled bonuses (per anomaly, relic, species, contact, megastructure, artificial world, stored food, food income,
  Resort Worker, Tourist) apply as described; agendas appear after finishing their tree; each anomaly researched with Anomaly Studies gives 5 minor artifacts.
- Species Experimentation: only Evolutionary Predators who finished Mutation see it; your main species and its subspecies are never offered;
  under 100 pops it's greyed out; picking a species kills half of it, creates 50 subspecies and costs 1000 unity.
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
