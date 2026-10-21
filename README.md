# LFG Traditions

A Stellaris **4.5** mod for **Gigastructural Engineering & More (4.5)** games that adds:

- **9 tradition trees**, each with a hook that scales with your game state, available only to fitting empires.
- **6 council agendas** unlocked by the trees (The Great Project has two versions, with and without supertensiles).
- **4 ascension perks:** **Mothership** (needs Nanite Armada, A Celestial Armada and Nanotech finished) unlocks the Progenitor Forge and the Mothership; **Nanite Armada** (needs Nanotech adopted) unlocks the Swarmforge megastructure and nanite Attack Moons and Planetcraft; **Curated Progress** (after Gigastructural Constructs) unlocks 27 **Shelve** edicts that stop specific repeatable techs from being offered as research options; **Massed Assault** gives +10 ground combat width and a general trait that boosts the armies they lead.
- **1 origin, Nanite Forge** (machines): eight size 40 molten worlds around a blue star, a broken nanite harvester that doubles their nanite deposits every 3 years, and a nanite-fuelled automation building.
- **Nanite harvesters** (all of them) yield **twice** vanilla's nanites at every step and get three more doubling steps, up to 819.2 nanites per planet.
- **Nanite Cognition Core** (after finishing Nanotech): automates 50% of a planet's specialist jobs for a lot of nanites.
- **Nanotensile Converter** (after finishing Nanotech, supertensiles on): turns energy and nanites into supertensiles.
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
  Vanilla allows 7 trees in total, and this mod adds 9 more options. Compatible with Expanded Stellaris Traditions and More Traditions (no shared keys).

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

### Stationcraft: wealth in orbit
**Who:** any empire. **Hook:** orbital stations (mining and research stations) produce more for every starbase (+2%),
kilostructure (+5%) and megastructure (+10%) you own, uncapped, but **jobs produce 35% less**. Layout `tree_12_12`
(Domestication's): a starbase branch (1 → 3) and a megastructure branch (2 → 5) that meet in slot 4.

| Tradition | Effect |
|---|---|
| Adopt ⚙ | Station output +3% per colony, +2% per starbase tier (outpost 1 … citadel 5), +5% per kilostructure, +10% per megastructure · resources from jobs −35% |
| 1. Orbital Logistics | Starbase capacity +3 · starbase upkeep −25% · starbase influence cost −25% |
| 2. Kilostructure Doctrine | Megastructure build speed +20% · megastructure cost −10% |
| 3. Bastion Starbases (needs 1) | Starbase hull and armour +25% · +3 defense platforms · starbase build speed +50% |
| 4. Orbital Refineries (needs 1 + 2) | Station output +15% · starbase building and module output +30% (`starbase_constructions_produces_mult`: vanilla has no buildings-only modifier) |
| 5. Self-Repairing Frames (needs 2) | Megastructure upkeep −20% |
| Finish | +1 megastructure under construction |

The counts are taken **once a month** (and on adoption) by `lfg_stationcraft.1` into country variables (`lfg_sc_*`), which
keeps four country modifiers (`lfg_stationcraft_per_colony` / `_starbase` / `_kilostructure` / `_megastructure`, shown in
the empire's modifiers) at `multiplier =` each count (`lfg_stationcraft_sync`, re-added when a count changes), so the
bonus can lag a month. (The tradition's own `triggered_modifier` with `mult = value:...` didn't grow in game.) Losing the
tree removes them on the next monthly run. Kilostructures are
Gigastructural's `is_kilostructure`; megastructures are every other owned megastructure that isn't ruined or technical
(Giga's `is_ruined_mega` / `is_technical_mega`); starbase tiers: outpost 1, starport 2, starhold 3, star fortress 4, citadel 5 (`has_starbase_size`), so upgrading adds up;
with **NSC3**, its stronghold counts 6 and headquarters 7 (`has_starbase_size > starbase_citadel` +1, `is_ship_size =
starbase_headquarters` +1; without NSC3 that ship size is unknown and the check is false, possibly with a log line). Colonies are every owned planet (`every_owned_planet`).

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
its main species. "Planet types" is the generated `value:lfg_count_world_types`, from every `colonizable = yes` planet class in vanilla
and Gigastructural (~50 checks). Every Shore reads it through a monthly cache: `lfg_lineage.1` (monthly, and on adoption)
stores it in the country variable `lfg_world_types`, read by `value:lfg_num_world_types`, so it can lag up to a month.

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
| Adopt | Resort Worker workforce +10%, resort district build speed +25% · psionic empires with the Instrument of Desire's **Exploitation** accord: Resort Workers count like Entertainers (+1% resources from jobs per 100 on their planet; generated `resort_worker` override) · unlocks agenda **Grand Tour Season** |
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

Unlocked by finishing the matching tree (The Great Project: by adopting Megaforge). Each has its own icon
(`interface/lfg_council_agendas.gfx`, `GFX_council_agenda_icon_<key>`; drawn by `art/make_glyph_icons.py`). Requires the Galactic Paragons DLC, like all vanilla agendas. The council
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

## Origin: Nanite Forge (machines)

**Who:** machine species, individual or gestalt (`species_archetype = MACHINE`), not nomadic. The homeworld gets a planetary
**Nanite Vein** deposit (`d_lfg_nanite_vein`, +15 nanites; not orbital), **50 nanites** to start with, and the founder species the **Nanite Substrate**
trait (`trait_lfg_nanite_substrate`, can't be added, removed or merged by species modification): pops **+20% job
efficiency** and **+0.3 nanites upkeep** (per 100 pops); mechanical pop assembly speed **−30%** where they're assembled (there is
no mechanical-only modifier). **Neither applies on a Nanite World** (`pc_nanotech`): the upkeep's `trigger` and the
assembly block's `potential` check the planet. The deposit is added at game start by `lfg_nanite_forge.1`; the trait through the origin's
`traits = { trait = trait_lfg_nanite_substrate }`, like vanilla's Evolutionary Predators (shown added and locked in the
species designer). Needs The Machine Age
(nanites and the Nanotech tree).
**Home system** (`lfg_nanite_forge_start`): a **blue B-class star** with a **+22 energy** deposit (`d_lfg_nanite_forge_star`,
mined by a mining station; set at game start by `lfg_nanite_forge.1`, because vanilla's home-system setup re-rolls the
star's deposits to +5 energy), a **size 12 homeworld** (the initializer says 10; the game makes home planets 12; with a moon; `lfg_nanite_forge.1` also removes **2,000 of its pops**, 100 at a time from the
largest pop group, `@lfg_nanite_forge_pops_removed_hundreds`), **eight size 60 molten worlds** evenly spaced on one orbit (one starts with a **+10 minerals** deposit, `d_minerals_10`), a **broken world with +8 engineering** and a **research
asteroid with +3 physics** (inner belt), another with **+5 society** (outer belt) (both flagged `ignore_startup_effect` so vanilla's home-system setup keeps their deposits), a
small molten world, barren, toxic, frozen and cold barren worlds with moons, two asteroid belts (12 asteroids) and a gas giant
with 3 moons.
**Starting starbase:** the origin starts with **Starholds** researched (`tech_starbase_3`) and the home starbase upgraded
to a Starhold (`lfg_nanite_forge.1`).
**Broken Nanite Harvester** (`lfg_broken_nanite_harvester`, starbase building): never buildable. At game start
(`lfg_nanite_forge.6`, fired by `lfg_nanite_forge.1` on `on_game_start_country`, and again a day later if it isn't there,
in case the game's own starbase setup overwrote it) it goes into the home starbase's first free building slot (number of buildings + 1); the slot is remembered as
star flag `lfg_broken_harvester_slot_<n>` for the restoration. Like vanilla's harvester it gives
every rocky body in the system without a research deposit a 0.1 nanite deposit and has vanilla's energy upkeep (4 per
grown deposit with a mining station; the star's 22 energy covers about 5), then (`lfg_nanite_forge.2`):
- doubles them **every 3 years** (vanilla: 5) with **no Nanotech requirement**, using vanilla's steps, size limits, odds and
  payouts (`lfg_forge_harvester_step`), and like vanilla only for planets with a **mining station**;
- stops at **step 7 (25.6 nanites per planet**, all harvester amounts here are doubled, see below**)**: on the molten worlds that's 8 × 25.6 = 204.8 nanites a month before modifiers.
- **Finishing Nanotech restores it** into the **Ancient Nanite Harvester** (`lfg_ancient_nanite_harvester`; swapped in the
  same slot by `lfg_restore_forge_harvester` from `lfg_nanite_forge.3` on `on_tradition_picked`, also checked every 3
  years). It's our own building, not vanilla's (whose `possible` would refuse a system where every rock already has a
  deposit), and keeps our 3-year cycle through the whole ladder: vanilla's steps 8-9, every harvester's steps 10-12, and
  four of its own: **step 13** (size ≥ 45, 1,638.4), **step 14** (size ≥ 50, 3,276.8), **step 15** (size ≥ 55, 6,553.6) and
  **step 16** (size ≥ 60, **13,107.2** per planet). Steps 13-14 use our `d_lfg_nanite_harvester_deposit_huge` (819.2 = 16
  of the (doubled) largest vanilla deposit) and steps 15-16 our `d_lfg_nanite_harvester_deposit_vast` (3,276.8) instead of dozens of
  deposits. Fully grown, the eight forge worlds make about **104,900 nanites a month** before modifiers.
  **Its upkeep is higher than vanilla's harvester**: **6 energy** per upkeep unit (vanilla: 4; `@lfg_ancient_harvester_energy`),
  and the units keep growing past vanilla's last step: vanilla's count (by the step a planet is on: 1, 2, 4 ... 256 at
  step 9; vanilla's steps replace their flag) **+256 per planet for each of steps 10-16** (`value:lfg_ancient_harvester_upkeep_units`,
  `@lfg_ancient_harvester_units_per_step`; our step flags add up). Fully grown: 2,048 units, **about 12,300 energy a month
  per forge world** (~98,000 for all eight) against ~13,100 nanites each. The broken harvester keeps vanilla's 4 per unit.
- Dismantling either clears the system's harvester deposits and step flags (`lfg_nanite_forge.4` →
  `lfg_clear_forge_harvester`), except during the swap (timed star flag `lfg_nanite_harvester_swapping`).
Neither can be built by hand: their `possible` only passes while our events place them (country flag
`lfg_placing_forge_harvester`). It **always doubles every 3 years**: the generated `cybernetics.5054` override makes
vanilla's 5-year cycle skip any system with it (e.g. a Nomad nanotech waystation parked there), and a generated
`nanite_harvester` override stops vanilla's Nanite Harvester from being built on the same starbase (fail text
`lfg_requires_no_ancient_harvester`). Elsewhere you can build vanilla harvesters once you've adopted Nanotech, as usual.

**No extra habitable worlds:** the origin replaces vanilla's guaranteed-colony neighbours (the game setting) with **two
science neighbours** (`lfg_nanite_forge_science_society_init`, 1-2 jumps away, and `_physics_init`, 1-3 jumps), and neither has a habitable world. Each is built for Gigastructural's three
research kilostructures, which each sit on a host world and put research deposits on every other "science candidate"
(`giga_is_science_candidate`: not a star, not colonizable, no mining deposit) in the system. It has the three hosts (a
**frozen** world for the Macroengineering Test Site → engineering, a **gas giant** for the Atmosphere Shredder → physics,
a **toxic** world for the Orbital Artificial Ecosystem → society) and 25-27 bare rocks, moons and asteroids: **28-30
bodies**, all with their deposits cleared, except one inner asteroid each: a **4 society** deposit (`d_society_4`) in the
first, a **3 physics** deposit (`d_physics_3`) in the second (both for research stations). Anomalies can spawn; Gigastructural's kilostructures need them researched first.

**Nanite Consensus** (`building_lfg_nanite_consensus_1` → `_4`, this origin only): unity from thinking nanites, **any
number per planet**, in capital or unity slots. Built for minerals and nanites, upkeep in energy and nanites; upgrades
three times. **Each tier needs its society tech** (`tech_lfg_nanite_consensus_1` → `_4`: Nanite Consensus, Consensus
Arrays, Lattices, Cores; tiers 1-4, each needing the last; the first offered at game start by `lfg_nanite_forge.1`).
Per tier (`@lfg_nanite_consensus_*`):

| Tier | Unity | Cost (minerals / nanites) | Upkeep (energy / nanites) |
|---|---|---|---|
| Node | 10 | 300 / 50 | 8 / 2 |
| Array | 20 | 400 / 100 | 16 / 4 |
| Lattice | 40 | 500 / 200 | 24 / 8 |
| Core | 60 | 600 / 400 | 32 / 16 |

Icons (`art/make_building_icons.py`): vanilla's mechanical Brain Node without its research flask, its undergrowth turned to
grey goo, with vanilla's unity symbol and 1-4 tier pips. **Replicators:** with this origin every replicator job costs
**+0.5 nanites** upkeep (per job, i.e. per 100 pops working it; generated override of vanilla's `replicator` job,
`common/pop_jobs/zz_lfg_job_overrides.txt`, `@lfg_nanite_forge_replicator_upkeep`).

**Nanite Automation Hub** (`building_lfg_nanite_automation`, this origin only, needs the engineering tech **Nanite Automation** (`tech_lfg_nanite_automation`, tier 1, offered at game start), one per planet, in an energy, mining or
farming specialization like vanilla's automation buildings): automates **50%** of Technician, Miner and Farmer jobs (and
their drone versions), through the static modifier `lfg_nanite_hub_automation` (one tooltip line; kept on planets with
the building active by the monthly `lfg_nanite_forge.5`, like the Cognition Core's). Costs 600 minerals + 100 nanites; upkeep **30 nanites per resource district** on the planet
(`value:lfg_resource_districts`: energy, mining and food districts, including habitat, ring world, machine, hive and ark
versions). Automated jobs still pay vanilla's automation upkeep. On a **Nanite World** (`pc_nanotech`) it costs **half**
(build cost and upkeep; `@lfg_nanite_world_discount`), like the Cognition Core. It can stack with vanilla's own automation buildings.

## Buildings: Nanite Freight (Nanite Forge origin)

`building_lfg_nanite_freight_1` → `_2` → `_3` (**Relay**, **Network**, **Lattice**): this origin only, **one per
planet**, in a city or capital slot (trade category). Pays nanites for trade, to offset planetary logistics costs:

| Level | Nanites upkeep | Trade | Build cost (minerals / nanites) | Tech (engineering) |
|---|---|---|---|---|
| Relay | 10 | 150 | 300 / 50 | `tech_lfg_nanite_freight_1` (tier 1; offered as a research option at game start by `lfg_nanite_forge.1`) |
| Network | 20 | 300 | 500 / 100 | `tech_lfg_nanite_freight_2` (tier 2) |
| Lattice | 30 | 450 | 800 / 200 | `tech_lfg_nanite_freight_3` (tier 3) |

Tunables: `@lfg_nanite_freight_*`. Icons (`art/make_building_icons.py`): vanilla's Commercial Zone, Forum and Megaplex in
nanite colours with the nanite and trade symbols; the techs show the Relay.

## Building: Nanite Cognition Core (Nanotech)

`building_lfg_nanite_cognition_core`: any empire that has **finished Nanotech** and researched **Nanite Cognition** (`tech_lfg_nanite_cognition_core`, society tier 3, drawn once Nanotech is finished); one per planet, in a city or capital
slot. Automates **50% of every specialist and complex drone job** on the planet (vanilla and Gigastructural, ~220 jobs).
Costs 1,000 alloys + 500 nanites; upkeep **500 nanites per district** (both **halved on a Nanite World**) (any kind, `value:lfg_all_districts`) a month. The job list is the generated static modifier
`lfg_nanite_specialist_automation` (`tools/gen_overrides.py`, one tooltip line), which the monthly `lfg_nanite_forge.5`
keeps on planets with the building **active** (`has_active_building`: disabling or ruining it removes the automation
within a month; the game has no on_action for toggling a building). Tunables: `@lfg_nanite_core_*`, `@lfg_nanite_hub_*`.

**Upgrade: Nanite Overmind Core** (`building_lfg_nanite_cognition_core_2`): needs **Nanite Overmind**
(`tech_lfg_cognition_core_2`, a society research option the **Mothership** perk adds). Automates **100%** of every
specialist and complex drone job (generated `lfg_nanite_specialist_automation_full`; the monthly check swaps the 50%
modifier for it). Costs 2,000 alloys + 1,000 nanites; upkeep **1,000 nanites per district** (both halved on a Nanite
World). Tunables: `@lfg_nanite_core_2_*`.

**Logistics offset:** the Automation Hub and both Cores also produce **trade = 1.875 × their nanite upkeep** (per district,
`@lfg_nanite_*_trade_per_district`: 56.25 / 937.5 / 1,875): 75% of the planetary logistics cost of that upkeep when the
planet is short of nanites (vanilla charges 2.5 trade per nanite of a planet's deficit). On a Nanite World the upkeep and this trade are
both halved (`@lfg_nanite_*_per_district_nanite_world`). Icons (`art/make_building_icons.py`): the Automation Hub is vanilla's Automation building in nanite colours;
the Cognition and Overmind Cores vanilla's Nanite Transmuter with a glowing cyan core (the Overmind crowned by a ring).

## Building: Nanotensile Converter (Nanotech, supertensiles)

`building_lfg_nanotensile_converter`: any empire that has **finished Nanotech**, only while Gigastructural's job-based
supertensiles are on (global flag `giga_buildcap_j`); any number per planet, in the same slots as Gigastructural's megaworkshops
(industrial, factory, foundry, capital and supertensile specializations). Costs 500 alloys + 250 nanites; each month turns
**40 energy + 80 nanites into 8 supertensiles** (`@lfg_nanotensile_*`). **Upgrades once** to the **Nanotensile Foundry**
(`building_lfg_nanotensile_converter_2`: 1,000 alloys + 500 nanites; **80 energy + 160 nanites into 16 supertensiles**,
`@lfg_nanotensile_2_*`). Icons (`art/make_building_icons.py`): Gigastructural's megaworkshop with the nanite and
supertensile symbols side by side; the Foundry's glows.

The origin's broken and Ancient harvesters are **never offered** in a starbase's (or Gigastructural deep space citadel's)
build list: their `potential` needs the country flag our events set only while placing them. The Ancient harvester has its
own module icon (vanilla's harvester in ancient bronze with a nanite glow, `art/make_building_icons.py`). **Unverified in
game:** that a `potential` failing later leaves a built one in place.

The in-game origin texts deliberately don't describe the home system; its start-screen name is `lfg_nanite_forge_start_NAME`.

**Unverified in game:** that the game-start placement sticks (the retry a day later covers it; the first version failed
because its `possible` was `always = no`, which `set_starbase_building` also checks); that the swap to the Ancient harvester doesn't fire the broken one's `on_destroyed` before the timed flag is seen
(the flag guards it); the size 40 molten worlds' layout.

## Nanite harvesters: twice the nanites, three more steps

Every harvested nanite deposit yields **twice** vanilla's amount (generated `common/deposits/zz_lfg_deposit_overrides.txt`:
vanilla's three harvester deposits, 0.1 / 1.6 / 25.6, each get a second equal `produces` block), so a harvester's first
step and every step after are doubled. All amounts below are the doubled ones.

Vanilla doubles harvested nanite deposits every 5 years up to step 9 (102.4 per planet, size 25+). A generated override of
`cybernetics.5054` adds **step 10** (size ≥ 30, 50%: 204.8), **step 11** (size ≥ 35, 50%: 409.6) and **step 12** (size ≥ 40,
50%: 819.2) for every harvester, before vanilla's payout for planets that can't grow (sizes: `@lfg_nanite_step_1x_size`).
Planets keep `nanites_doubled_9`, so vanilla's upkeep and payouts still count them; the new steps use
`lfg_nanites_doubled_10/11/12`, which the `cybernetics.5051` override clears when a harvester is removed. Only planets of
size 30+ (vanilla's largest rocky worlds are smaller; the Nanite Forge's molten worlds are 40) can use them.

## Decision: Nanite Pulse (Nanotech)

`decision_lfg_nanite_pulse`, for any empire that has **adopted Nanotech**, taken **from a star** (Gigastructural's pattern:
`owned_planets_only = no`, `is_star = yes`, the system is ours) whose system's starbase has a **nanite harvester**
(vanilla's, or the Nanite Forge's broken / Ancient one). Costs **10,000 nanites per celestial body** in the system
(`value:lfg_nanite_pulse_bodies`: `count_system_planet` with `trigger_scope = solar_system`, the star included); the star can
pulse again after **1,000 days** (timed planet flag). Then **a coin for every body**: heads, a world that can grow (a mining
station on a harvested deposit) **grows one harvester step** (`lfg_forge_harvester_step`; with vanilla's harvester it may
take steps 8-12 too, steps 13-16 stay the Ancient harvester's); tails, or a world that didn't grow (no station, or already
at its last step), **12 months of that body's harvested nanites** (the in-game text only says it's based on deposit size) (`value:lfg_pulse_deposit_nanites` × `@lfg_nanite_pulse_payout_mult`:
its harvester deposits counted with `count_deposits` (`type =`; a `limit` there is ignored, which once paid out every deposit at every size), at the doubled amounts; nothing without one), times the empire's
mining station nanite multiplier (1 + `station_gatherers_produces_mult`, `station_gatherers_nanites_produces_mult`,
`stations_produces_mult`, `stations_nanites_produces_mult`, `country_nanites_produces_mult`, read with
`export_modifier_to_variable`). Modifiers on a single station or planet aren't included. So early pulses cost
more than they return, and pulses on grown systems pay back. A world counts as grown only if its step count went up
(`lfg_count_nanite_steps`: the highest step flag, before and after; vanilla's steps replace their flag). One popup (`lfg_nanite_pulse.1`) reports the worlds grown, the nanites paid
back and the cost. Icon: vanilla's pulsar decision icon in nanite cyan (`art/make_megastructure_icons.py`). **Unverified in
game:** the decision showing on stars.

## Civic: Applied Biosciences

**Who:** Materialist or Fanatic Materialist empires whose species isn't a machine (gestalts can't be materialist).
**Effect:** per Biologist job: society research **−1** (3 → 2), physics **+0.4**, engineering **+0.4** (vanilla's
`planet_biologists_*_research_produces_add`, so Biologist bonuses and job efficiency apply to all of it). The Biologist job's
variants (Rangers, Xeno-Zoo Keepers, Stratovent Researchers, Archaeo-Engineers) count too. Icon: vanilla Genetic Identification
recoloured to the mod's amber civic colour (`art/make_civic_icons.py`; every civic from this mod uses it).
**Council position:** **Chief Bioengineer** (scientists only; `councilor_lfg_applied_biosciences`): Biologist job efficiency
**+3% per level**. Not more physics per Biologist, because vanilla's Technocracy councilor (also Materialist) already gives that.

## Galvanic upgrades (galvanic civics)

Any empire with a galvanic civic (`is_galvanic_empire`, non-bio ships, like vanilla's lines) can draw two tier 5
engineering techs (`common/technology/lfg_technology.txt`, cost `@tier5cost3`, weight `@tier5weight3`):
- **Symbiotic Accelerators** (`tech_lfg_lm_accelerator_2`, needs `tech_kinetic_artillery_2`) → `LFG_LM_ACCELERATOR_2`,
  level 2 of the Reshaping Projectile Accelerator (large): **350-1,050** damage every 45 days (vanilla 165-500 / 50),
  range 140 (120), accuracy 90% (85%), 75% armour penetration (50%), 3x shield damage (2.5x), power -120 (-91). Cost
  1,000 living metal + 10 volatile motes (vanilla 333 + 3.5); upkeep 6 energy, 1.2 alloys.
- **Symbiotic Galvanic Armour** (`tech_lfg_lm_armor_6`, needs `tech_ship_armor_5`) → `LFG_{SMALL,MEDIUM,LARGE}_LM_ARMOR_6`,
  level 6 of the galvanic armour: **400 / 1,200 / 3,600** armour (vanilla level 5: 260 / 780 / 2,340), +2% armour and
  hull regeneration (1%), +2% energy weapon fire rate (same as level 5), 6% hardening (4%). Cost 160 / 400 / 1,000 living metal
  (vanilla 53 / 133 / 333).

## Ascension perk: Massed Assault

**+10 ground combat width**: more armies fight at the same time. **Every general** also gets the **Massed Assault Doctrine**
trait (`leader_trait_lfg_massed_assault`; given on taking the perk and to every new leader via `on_leader_spawned` →
`lfg_massed_assault.1`): armies they lead get damage **+25%**, health **+25%**, morale **+50%** (`@lfg_massed_assault_general_*`). Base width is 5 + 0.2 × planet size (size 10: 7,
size 20: 9, size 25: 10), so this roughly doubles it; the only vanilla source is general traits (+1, +2, Paragon +10).
Requires **4 other ascension perks** first. The AI never takes it. Amount: `@lfg_massed_assault_width`.
**Unverified in game:** vanilla only uses `planet_combat_width_add` on generals, so check that the perk's country-wide
modifier reaches your invasions (the width shown in ground combat).

## Ascension perk: Nanite Armada

`ap_lfg_nanite_armada`: like Gigastructural's **A Celestial Armada**, with the same requirements (Gigastructural
Constructs, 3 other perks, War Planets and Tetradimensional Engineering) **plus the Nanotech traditions adopted** (its
costs are all nanites). AI never takes it. Like Celestial Armada, it
adds research options you still have to research, all **Engineering** (voidcraft; never drawn without the perk, weight 0):
**Swarmforge** (`tech_lfg_swarmforge`, 48,000), **Nanite Attack Moons** (`tech_lfg_nanite_war_moon`, 64,000) and
**Nanite Planetcraft** (`tech_lfg_nanite_planetcraft`, 96,000), which unlock (nanite storage has no cap, so
the 1,000,000-nanite Planetcraft needs no storage bonus):

- **Swarmforge** (`lfg_swarmforge_0` site → `lfg_swarmforge_ready`): a giant nanite shipyard built around the star of a
  system in your borders with a **class A or B star or a red giant** (`lfg_swarmforge_star`) and no other megastructure.
  Site: 10,000 alloys, 50,000 nanites, 100 influence, 5 years; finishing it: 25,000 alloys, 150,000 nanites, 10 years;
  upkeep 100 energy + 50 nanites. Finished, it's a shipyard (`starbase_shipyard_capacity_add`, like vanilla's Mega
  Shipyard; `@lfg_swarmforge_shipyard_capacity` = 50). Finished, it also gives the **whole empire** shipyards **+100% build
  speed** (`starbase_shipyard_build_speed_mult`) and ships **-10% cost** (`ships_cost_mult`). **Its model** (`mod/gfx/models/ships/lfg_megastructures.asset`)
  is built **over the star**: a nanite cage of six great circles of 12 Nanite Swarmers meeting at the poles, four nanite
  hive stations on the equator as docks and four grey goo clouds (under construction: three circles and the docks);
  sizes `@lfg_swarmforge_*scale`. Build icon: `art/make_megastructure_icons.py` (vanilla's Mega Shipyard tech icon in
  nanite cyan with the Nanites symbol).
- **Nanite Attack Moon** (`lfg_nanite_war_moon`, **500,000 nanites**) and **Nanite Planetcraft** (`lfg_nanite_planetcraft`,
  **1,000,000 nanites**): Gigastructural's Attack Moon and Planetcraft models with twice their hull and armour and half
  their shields (moon 500K hull / 300K armour / 50K shields; planetcraft 5M / 2.5M / 625K), size 64 / 128 (`size_multiplier`;
  Giga's: 250 / 750), **nanites only**: components add nothing to cost or upkeep (`components_add_to_cost = no`),
  upkeep in energy and nanites,
  built like normal ships but **only at a Swarmforge or Progenitor Forge** (`lfg_is_swarmforge`: the shipyard must be one
  of those megastructures). The Swarmforge builds 50 at once (`@lfg_swarmforge_shipyard_capacity`).
  **Designable** in the ship designer: their sections are generated copies of Giga's
  (`common/section_templates/lfg_nanite_section_templates.txt`), and a generated override adds them to Giga's
  `giga_ship_uses_war_moon_components` / `giga_ship_uses_war_planet_components`, so Giga's moon / planet reactors,
  computers and weapons fit.

**Their look**: Giga's moon and planet meshes with nanite planet textures (generated
`mod/gfx/models/ships/lfg_nanite_celestials.asset`), dressed in our own designs from vanilla's nanite (Gatebuilder) ships
(`mod/gfx/models/ships/lfg_nanite_hulls.asset`; sizes `@lfg_moon_*` / `@lfg_pc_*`, first guesses). **The ship designer
shows them** because the look is in a section: the moon's stern sections are the moon itself, and the planetcraft's (and
the Mothership's) mid section model holds Giga's weapon locators plus the look (`SECTION_BODIES` in the generator), while
the hull model is an invisible frame (Giga put the look on the hull model, which the designer doesn't draw). The moon
has no swarm: in game it showed as a dark blob hiding the moon.
- **Nanite Attack Moon:** drawn smaller than Giga's moons (`NANITE_MOON_SCALE` 0.5 vs Giga's 0.8). Its default sections are a **Grey Goo** moon (the Grey Goo world's surface). Giga's optional
  planet-skin sections (behind its Aeternite tech) are replaced by two nanite skins with no tech: **Machine Shell**
  (synthetic ecumenopolis surface) and **Swarm Core** (machine world surface). Section names: generated
  `lfg_nanite_sections_l_english.yml` (Giga's names for the copied sections). Every skin has an **escort**: a tilted
  ring of 8 small Nanite Swarmers close around it (`lfg_nanite_moon_escort_entity`).
- **Nanite Planetcraft:** the grey goo world with an equatorial ring of 12 Nanite Interdictors, a tilted ring of 16
  Nanite Swarmers, nanite hive stations capping both poles and the grey goo swarm (`lfg_nanite_planetcraft_mid_entity`;
  `graphical_culture = no`, so not Giga's species-culture planets).
- The swarm's size is `@lfg_nanite_swarm_planet_scale` / `@lfg_nanite_swarm_mothership_scale` in the generator's
  `NANITE_SWARM_ENTITIES` (a first guess: check it in game and adjust).

**Unverified in game:** that the megastructure's shipyard offers only these hulls and builds them; the nanite look (the
swarm's size around each hull, and Giga's moon mesh with the grey goo texture); the Swarmforge's model
over its star; the designer showing the section-held looks; that the three techs stay research options after a reload (`add_research_option`, like Giga's).

## Ascension perk: Mothership

`ap_lfg_mothership`: needs both **Nanite Armada** and Gigastructural's **A Celestial Armada**, and the **Nanotech
traditions finished** (its escort's Swarmers and Interdictors need the 4th and 5th). AI never takes it. Adds two
**Engineering** research options (voidcraft, weight 0): **Progenitor Forge** (`tech_lfg_progenitor_forge`, 160,000) and
**Motherships** (`tech_lfg_mothership`, 256,000).

- **Progenitor Forge** (`lfg_progenitor_forge_0` → `_1` → `_2`): built around an **O-class star** (Gigastructural's
  `giga_is_o_star_for_megas`: its own O stars, about 1 per 70 systems, and Real Space's), in your borders, with no other
  megastructure. Three stages, **50,000,000 nanites** in all (5M, 15M, 30M; `@lfg_progenitor_forge_*_nanites`) plus
  alloys and influence; 5 + 10 + 10 years. Finished, it's a shipyard building **300 ships at once** (`@lfg_progenitor_forge_shipyard_capacity`), the only place
  Motherships can be built, and it also builds the nanite Attack Moons and Planetcraft.
  **When its site (stage 1) is done, its swarms consume the system**: every world Gigastructural allows to be dismantled
  for bulk matter (`can_dismantle_planet_for_bm`: not the star, colonies, habitats, megastructure anchors, holy worlds...)
  gives its builder **1 bulk matter per size** (Giga's rate) and is removed, along with the debris and asteroid belts
  (`lfg_progenitor_forge_consume_system`, popup `lfg_mothership.10` with the total). Popups also mark stage 2
  (`lfg_mothership.11`), the finished forge (`.12`) and a finished Mothership (`.13` → `.14`). Icon (tech and build menu):
  an O-class star in two nanite rings (`art/make_glyph_icons.py`). **Unverified in game:** `remove_planet` from a
  megastructure's `on_build_complete`.
  Its model (`mod/gfx/models/ships/lfg_megastructures.asset`) is built **around the star**, laid out like Gigastructural's
  Hyperstructural Assembly: stage 1 is a ring of 12 nanite (Gatebuilder) space stations with six grey goo clouds
  (`gray_goo_planet_effect`); the finished forge adds Giga's assembly yards and tractor beams and an outer ring of 12
  nanite motherships (the Nanite Interdictor model). **Unverified in game:** its size around an O star
  (`@lfg_progenitor_forge_*scale` at the top of the asset).
- **Progenitor Forge bonuses** (finished, `lfg_progenitor_forge_2`): **the forge itself builds +300% faster**
  (`station_modifier`), and the **whole empire** gets ships **+50% speed** (`ship_speed_mult`), **+10,000 naval capacity**
  and **+500 command limit** (`country_modifier`).
- **Mothership Swarm Core** (`LFG_MOTHERSHIP_REACTOR`, the Mothership's reactor, auto-picked: weight 100,000 over Giga's
  systemcraft reactor's 10,000; 2,000,000 power): carries its **built-in aura**, like the Juggernaut's reactor: **Swarm
  Link**, every friendly ship in its system (the Mothership too) **+25% speed** and **+25% kinetic weapon fire rate**
  (`@lfg_mothership_aura_*`). A designer could still swap in Giga's reactor and lose it.
- The **Mothership tech** lists its 13 components as one line (*Unlocks Components: Nanite weapons, armour, hangars and
  swarm modules*): each has `show_tech_unlock_if = { always = no }` and the tech a custom `prereqfor_desc` line.
- **Mothership** (`lfg_mothership`, **one per empire**, **100,000,000 nanites + 500,000 alloys + 700 influence + 100 bulk matter** (Gigastructural's) **and a crew of 2,000 pops** (like Giga's systemcraft's 4,000: the planet decision `decision_lfg_mothership_crew`, on a world with more than 2,000 pops, takes them and sets the flag its construction needs; a finished Mothership uses it up), upkeep a flat **30,000 nanites** a month: components add
  nothing to cost or upkeep, `components_add_to_cost = no`; 10 years): 100M hull, 24.2M armour, 3M shields (Gigastructural's
  systemcraft: 12.5M / 4.8M / 1.9M), size 256 (`size_multiplier`; the systemcraft: 1,250), speed 100 (the systemcraft: 30), **2x jump drive range** (`ship_ftl_jumpdrive_range_mult = 1`; hidden: not on the Steam page). One per empire: `possible_construction` (at the Progenitor Forge, so designing
  stays open; `possible_country` also blocked the designer) blocks queueing another while you own
  one, and `lfg_mothership.6` (`on_ship_built`) deletes a second that was queued alongside and refunds its hull cost. Its sections are generated copies of Giga's systemcraft sections with the mid
  section's guns turned into hangars (**45 hangars**) and **4 aux utility slots in every section** (24; `MOTHERSHIP_AUX_SLOTS`); Giga's systemcraft components fit (generated trigger override).
  Its sections have Mothership names (`MOTHERSHIP_SECTION_NAMES`, by slot): Disassembler Prow (the bow with the W slot),
  Siege Prow, Siege Driver Battery, Nanite Hive Bays, Reshaper Spine, Swarm Brood Decks, Swarm Heart.
  **Its look** is our own (`mod/gfx/models/ships/lfg_mothership.asset`, no systemcraft model): a **Swarm Core** world at
  the centre (Giga's planetcraft mesh in the machine world skin, generated as `lfg_mothership_core_entity`), three
  gyroscope rings of 12 Nanite Interdictors tilted 60 degrees apart around its long axis, nanite hive stations as prow
  and stern, a halo of 24 Nanite Swarmers, the grey goo swarm and Giga's systemcraft thruster plumes. Weapons fire from
  Giga's systemcraft weapon locators. **Unverified in game:** the parts' sizes and placement (`@lfg_ms_*_scale`).
- **Nanite Swarm hangar** (`LFG_NANITE_SWARM_HANGAR`, Motherships only, `common/component_templates/lfg_components.txt`):
  strike craft can be buggy, so **few but strong**: 2 craft per hangar (90 in all; 0.5 rebuilt a day), 125-225 damage every 1.5 days, 400
  health, 200 armour, 500 shields, full shield penetration. For comparison, ACOT's Alpha-tier best: fighters 8 craft,
  12-34 damage every 2 days, 17 health; bombers 4 craft, 423-507 every 14 days.
- **Nanite Reshaper** (`LFG_NANITE_RESHAPER`, X slot, Motherships only): the Reshaping Projectile Accelerator
  (vanilla `LM_ACCELERATOR`) rebuilt from nanites (20,000 nanites, 10 upkeep): kinetic, **2,500-6,250** damage every
  50 days (windup 9-34), range 180, accuracy 90%, 40% armour and shield penetration, 2.5x shield damage, no power.
  ACOT's Alpha X kinetic for comparison: 1,996-5,232 every 80 days, range 175, accuracy 75%, 50% shield penetration.
- **Swarm modules** (aux "A" slots, Motherships only, 5,000 nanites each, free on the Mothership): each adds to the
  Mothership's swarm reserve, and they **stack per module**: **Swarmer Hive Vault** (`LFG_SWARMER_VAULT`) +100 swarmer
  storage, **Swarmer Foundry** (`LFG_SWARMER_FOUNDRY`) +20 swarmers a month, **Interdictor Hive Vault**
  (`LFG_INTERDICTOR_VAULT`) +40 interdictor storage, **Interdictor Foundry** (`LFG_INTERDICTOR_FOUNDRY`) +6 interdictors a
  month (`@lfg_*_vault_add` / `_foundry_add`). How: each gives a custom ship modifier (`common/scripted_modifiers/
  lfg_scripted_modifiers.txt`: `lfg_mothership_swarmer_storage_add` etc.); `lfg_mothership.2` reads the Mothership's
  summed values with `export_modifier_to_variable` (`lfg_mothership_add_module`) and adds them to the base 80 / 20 a
  month and 600 / 200 caps. **Unverified in game:** that component `ship_modifier`s of custom modifiers reach the ship.
- **Nanite Armour** (`LFG_NANITE_ARMOR`, large utility, **any ship**, **10,000 nanites + 15 nanites/month** per plate
  (`@lfg_nanite_armor_cost` / `_upkeep`; free on the Mothership, whose components add nothing)): per plate, split evenly
  between armour and hull: +12,500 armour and +12,500 hull, +1% armour and +1% hull regeneration, +50 armour and +50
  hull flat regeneration; plus +6% armour hardening, **+6 damage reduction** (`ship_damage_reduction_add`; vanilla
  crystal plating gives 1-4) and **+3% kinetic weapon fire rate** (stacks per plate).
- **Nanite Siege Driver** (`LFG_NANITE_SIEGE_DRIVER`, **T slot**, the Mothership's special weapon, from the Mothership
  tech): **any number on a Mothership, at most 3 on a Maginot World** (Gigastructural's `strategic_defence_command_platform`;
  a twin template `LFG_NANITE_SIEGE_DRIVER_MAGINOT` with `ship_limit = 3`, same name and stats), nothing else. Kinetic,
  **30,000-80,000** damage every 60 days (windup 10-40), range 250, accuracy 95%, 75% armour and shield penetration,
  1.5x armour and 2.5x shield damage, no power. **On hit** (copied from ACOT's Titan Accelerator Cannon): the target
  gets **Nanite Infestation** (`lfg_nanite_siege_driver_debuff`: -20% armour and shield hardening, 180 days), and every
  hostile ship within 45 of it takes **7,500-15,000** damage (`@lfg_nanite_siege_driver_burst_*`). 100,000 nanites + **1,000 nanites/month** (`@lfg_nanite_siege_driver_*`;
  only a Maginot World pays it).
- **Nanite Storm Autocannon** (`LFG_NANITE_STORM_AUTOCANNON`, **L slot**, kinetic, from the Mothership tech): an upgrade
  of vanilla's large Nanite Autocannon for **every nanite hull** (vanilla's Nanite Swarmers and Interdictors, Nanite
  Attack Moons, Planetcraft, Mothership): the same profile (windup 2-8, 12-day cooldown, 85% accuracy, 25% tracking,
  1.5x shield / 0.25x armour damage) with **4x range (160 vs 40)**, **2.5x damage (255-525 vs 102-210)** and **2x hull
  damage** (vanilla 1.25x),
  no power; 1,000 nanites + 1 a month (free on those hulls: their components add nothing).
- **Nanite Disassembler** (`LFG_NANITE_DISASSEMBLER`, **W slot** World Cracker, Motherships only, the default pick:
  `ai_weight` 1,000): fires like Gigastructural's systemcraft World Cracker (30-day windup) and cracks whatever vanilla's
  World Cracker can (`can_destroy_planet_with_LFG_NANITE_DISASSEMBLER`). It turns the world into nanites for its owner:
  **+5,000 per size of the world and +5 per pop on it** (`value:lfg_disassembler_nanites`,
  `@lfg_disassembler_nanites_per_*`), paid by `lfg_mothership.7` before the world is cracked; that event then fires
  vanilla's `on_destroy_planet_with_PLANET_KILLER_CRACKER` (`.8` / `.9` pass on the queued / unqueued on_actions), as
  Giga's `giga_planet_killer_event_delegate` does. **Unverified in game:** that the pops are still counted when it fires.
- **Nanite Flak Swarm** (`LFG_NANITE_FLAK_SWARM`, point defence, **Motherships and Maginot Worlds only**): 38-75
  damage every half day (cooldown 0.5), range 45, 100% accuracy and tracking (vanilla Point Defence III: 4-8 every 5 days, range 30, 75%).
  5,000 nanites + 5 nanites/month (`@lfg_nanite_flak_swarm_*`).
- **Icons** (`art/make_component_icons.py`, `interface/lfg_components.gfx`): vanilla's armour plate, fighter, Reshaping
  Projectile Accelerator, Giga Cannon and point defence icons without their tier numerals, recoloured to nanite metal
  with glowing cyan, the Nanites symbol and drifting motes (the hangar shows a swarm of three fighters).
- **Nanite swarm** (`events/lfg_mothership_events.txt`): each Mothership keeps a **reserve** of Nanite Swarmers and
  Nanite Interdictors (fleet variables `lfg_swarmers` / `lfg_interdictors`) that grows by **80 / 20 a month**
  (`lfg_mothership.1` → `.2`), up to **600 / 200** counting deployed ships (`@lfg_mothership_*`). It's deployed **only
  while an enemy is in its system**: when the Mothership enters a battle (`on_entering_battle` → `.3` → `.4`) the reserve
  launches as an escort fleet (random picks from your designs) that follows it (`auto_follow_fleet`) and takes no naval
  capacity; monthly growth during the fight joins it. Every 5 days (`.5`) it checks for hostile ships in the system;
  once none are left, the survivors return to the reserve and the escort vanishes. Vanilla only gives designs for these
  with the Nanotech traditions (Swarmers: 4th, Interdictors: 5th); the perk needs Nanotech finished. The escort is tied
  to its Mothership by fleet flag `lfg_escort_of_@<fleet>`.

Verified in game: `create_ship` adds ships to an existing escort fleet (vanilla only uses it inside `create_fleet`).
**Unverified in game:** the escort deploying on battle, following its Mothership and being recalled once the system is
clear; the Mothership's look and swarm size.

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
| Starbase building `nanite_harvester` | Added: can't be built on a starbase with the Nanite Forge's harvester |
| Events `cybernetics.5054`, `cybernetics.5051` (nanite harvester doubling / removal) | Added: skips systems with the Nanite Forge's harvester; steps 10, 11 and 12 (see [Nanite harvesters](#nanite-harvesters-three-more-steps)); removal clears their flags |
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
