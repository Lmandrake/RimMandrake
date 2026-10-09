# CANON_MATERIALS_DESIGN_1 — canon Star Wars materials: what they are for and where they come from

2026-10-09. **Decided design**, the single source of truth for canon materials. Built under
`CANON_MATERIALS_BUILD_1` and the split items of §6. Points still marked **TO CONFIRM** are proposals the
owner has not ruled on.
The jobs × materials layout is `Transient/canon_materials_jobs_layout_2026-10-09.html`.
Placement numbers live in `design/RimMandrake/mineral_abundance_registry_2026-10-03.csv`; this doc decides
*roles* and *channels*, the registry carries the amounts. Canon research behind the fabrication routes:
`design/RimMandrake/canon_metal_fabrication_2026-10-09.md`. The census of our own materials:
`design/RimMandrake/exotic_materials_census_2026-10-09.md`.

## 0. Rulings this design rests on

- Owner typed 2026-10-09 07:05, on what materials serve: *"1+3. Having some materials only be tradable
  connects you to the greater Star Wars universe. And having a planet mining out every possible interesting
  mineral makes no sense, so salvage routes make a great deal of sense. But your comment about FOR THIS GAME,
  it's mostly about recovery, refiting, repair, and occasionally hacking together something that requires some
  of these rare materials. A planet filled with old broken salvage from massive mining companies and ANCIENT
  war fleets. And trying to make one of those ancient ships actually fly: hard enough! But then there's the
  shiny new Empire with all of its modern tech side-by-side, and you can salvage there stuff too, but the
  systems aren't greatly compatible."* ⇒ the governing loop of §0a.
- Owner typed 2026-10-09, on making that incompatibility mechanical: *"Not a great idea, ignore"* ⇒ the two
  salvage sources (§0b) differ in flavour and origin only. No part standards, adapters, mismatch penalties or
  strip-only rules.
- Owner typed 2026-10-09: *"Apparently Plasteel is already Star Wars canon, I didn't know that, so we should
  not equate it with any other Star Wars material. Please redo the canon materials analysis you did but
  without my equivalence requirement for plasteel: let it be its own thing."* ⇒ plasteel is its own canon
  material, distinct from durasteel and every other canon metal.
- Owner typed 2026-10-09: *"Yes, hold hard rules, wait for census, AND look at how the factory ship is likely
  able to forge some of this stuff."* ⇒ the frame of material uses (§3.1) is accepted; the six key jobs of §4
  are **held as preferences**, not enforced.
- Decisions taken by question card 2026-10-09: durasteel is a new def of ours, `RSW_Durasteel`, and every
  donor durasteel converts into it (§3.2); stygium and coaxium get their defs now, as trade goods (§3.6).
- Owner typed 2026-10-09 on a card (a question, recorded as his steer): *"Re-melt salvage, but durasteel is
  just steel + a mineral, so that seems like it could fit on the ship smelter too?"* ⇒ salvage re-melt aboard
  is yes; durasteel from steel + zersium on the ship smelter is the proposed route, **TO CONFIRM** (§3.2).
- Owner typed 2026-10-09: *"Yes, I think we will need an alloy forge. Maybe even earlier, but the recipies will
  unlock later in the game for more difficult alloys. Durasteel earlier, plasteel later..."* ⇒ the alloy forge
  of §3.4. This **revises** the earlier card rulings that made durasteel and plasteel salvage and trade only:
  both are now also fabricated, durasteel early and plasteel late.
- Owner typed 2026-10-09, on doonium: *"Also asteroid ore"* ⇒ doonium is salvage, rare trade, and asteroid
  ore smelted aboard (§3.5).
- Owner typed 2026-10-09, on beskar: *"(1) and a quest with Blackstar allows you to access that rare
  individual, otherwise you just use the pieces you find. Never can reforge yourself, smelting destroys it
  (converts into other lesser ores), only the rare location can properly reforge."* ⇒ §3.7.
- Owner typed 2026-10-09, on transparisteel: *"So this is what we should be filtering or sifting from the fine
  desert sand in the extreme desert. The stuff you can use to make glass bottles and objects. The stuff we
  already use to make lenses. All of that should be this. Instead of glass make it transparisteel."* ⇒ §3.8.
- Owner typed 2026-10-09, on bronzium: *"Too close to just bronze. Lame. Drop from game."* ⇒ bronzium is
  removed (§3.10).
- Decision taken by question card 2026-10-09 (owner typed *"Both"*): phrik is trade AND a rare desert phrikite
  deposit smelted aboard (§3.5).
- Decisions taken by question card 2026-10-09 on the census merges: one chitin ladder; the 7 `RUT_`
  duplicates of `RM_` items dropped; one common salt with the 4 Grey Sea crystal salts kept as premium; the
  twin plasteel slags merged; the twin tibannas merged (§3.10).
- Decisions taken by question card 2026-10-09 on census roles: cloak lacquer is personal camouflage only;
  mindstone is the droid-mind crystal; krayt hide is an ordinary top leather (§3.9).
- Owner, 2026-10-09, on glower crust (relayed by BENCH): *"More lore than anything else but connects
  them"* ⇒ glower crust is an ingredient of doonium, which is what gives it trade value (§3.5).
- Owner typed 2026-10-09: *"I've ruled this before. All three will exist. Duranium and Doonium are mostly
  salvage and possibly rare trade."* (2026-10-03 typed: both made offworld, pretty rare, REQUIRED to build
  large ship and machine types such as factories.) Doonium's asteroid ore (above) adds to this.
- 2026-10-03 and 2026-10-09 (cards): precious metals and gems only in their home biomes; deep drilling = iron
  everywhere, everything else by home biome.
- 2026-09-25 typed: components and plasteel are never mined from rock; salvage is a major source of advanced
  materials.

## 0a. The governing loop

Materials in this game serve **recovery, refit and repair**, plus the **occasional hack** that needs a rare
material:

- **Salvage routes, not planet mining.** The planet does not hold every interesting mineral. Local mines give
  the basics (iron for steel, a few home-biome ores, Lantern Deeps kyber, the desert's fine sand and rare
  phrikite); asteroids add doonium ore; the advanced materials are pulled from wrecks and re-melted aboard.
- **The ship is a smelter, then a forge.** The factory ship melts scrap from the start (canon: the
  sandcrawler's reactor melts down scrap and droids). An alloy forge comes later and unlocks harder alloys
  progressively: durasteel early, plasteel late.
- **Trade-only materials tie the colony to the galaxy.** Stygium, coaxium, aurodium, corusca and chromium
  never appear on the planet. Phrik, transparisteel, doonium and duranium are also traded.
- **The rare-material hack is the peak moment.** Most work is patching things back together with durasteel,
  plasteel and components; a few repairs and refits need one stack of duranium, doonium, cortosis or beskar,
  and finding it is the expedition.
- **The flagship goal:** make one of the ancient ships actually fly. It should be hard.

## 0b. Two salvage sources (flavour and origin only)

| | **Ancient** | **Imperial** |
|---|---|---|
| what it is | wrecks of massive mining companies and ANCIENT war fleets, long dead and buried | the shiny new Empire's modern tech, deployed beside the old |
| where | Warscar troves, the Rust Cathedral, buried hulls, derelict mining rigs, B1 droid fields | crashed Imperial craft, outposts, patrol debris, orbital wreck salvage |
| typical yield | durasteel plate, plasteel droid shells, duranium frames, doonium reactor shielding, beskar and cortosis relics | plastoid armour, durasteel, plasteel housings, modern components |
| condition | heavily degraded; much is scrap, the rest needs restoration | mostly intact |
| canon flavour | Clone War B1s are plasteel; MagnaGuard frames are duranium; capital-ship cores are doonium-shielded | stormtrooper armour is plastoid; Death Star hull and core used doonium |

A part from either source fits any build. The sources differ in where they are found, how damaged the yield
is, and what it reads as; nothing in the rules checks which era a part came from.

## 1. Inventory — canon materials the game supports today

Method: a parse of every `Defs/**/*.xml` under `src/` for top-level defs whose defName or label names a canon
material (sanity probe: beskar returns 6 defs; durasteel 13), joined with the 2026-10-03 registry inventory
(26,589 ThingDefs from the live-set def dump, 73 mineral materials). `S` = has `stuffProps`. This is the
state before the build.

| material | defs that carry it today | form today | owner |
|---|---|---|---|
| plasteel | Core `Plasteel` (S, `Metallic`); KotOR smelt/slag recipes; crashed shuttles and `ShipChunk_durasteel` yield it | Core stuff | Core |
| durasteel | `KOTOR_AlloyDurasteel` (S), `KOTOR_MineableDurasteel`, `KotORChunk_durasteel` slag + smelt recipes, `ShipChunk_durasteel`, powered durasteel walls; `OuterRim_Durasteel`; `LKDurasteel_Ore` | alloy + ore | Armoury (ours), Outer Rim, LK |
| beskar / Mandalorian iron | `KOTOR_RawBeskar`, `KOTOR_IngotBeskar` (S), `KOTOR_MineableBeskar`, `kotor_IngotBeskar_recipe` (+10×); Outer Rim `OuterRim_Beskar`, `OuterRim_PureBeskar` (+ floors); LK `LKBeskar_Ore`; `guy762_crystalitem_beskar` | ore + ingot + stuff | Armoury, Outer Rim, LK |
| cortosis | `KOTOR_IngotCortosis` (S), `KOTOR_MineableCortosis`, `guy762_armband_cortosis` | ingot | Armoury |
| bronzium | `KOTOR_AlloyBronzium` (S), `KOTOR_MineableBronzium`, `KotORChunk_bronzium` slag (also a junk-pile `mineableThing`), bronzium light battle armor; 4 placed things on the exported ship | alloy | Armoury |
| plastoid | `KOTOR_Plastoid` (S), smelt recipes | stuff | Armoury |
| kyber | `Force_KyberCrystal`, `Force_CrystalFormation_*` (Lantern Deeps scatter `RUT_LanternDeepKyberScatter`), synthetic/bled/cleansed crystals, kyber quests | crystal | SW The Force, ours |
| stygium | `KOTOR_StygiumCrystal`, `guy762_crystalitem_stygium`, stygium cloaking research | crystal | Armoury |
| tibanna | `KOTOR_Tibanna` + pipe net, `RUT_TibannaGas` (beldon shearing), `OuterRim_Tibanna` | gas / item | Armoury, ours |
| rhydonium | `KOTOR_RawRhydonium`, `KOTOR_Rhydonium` fuel, rhydonium reactors, drug chain | fuel + drug | Armoury |
| spice | `KOTOR_Spice`, `KOTOR_MineableSpice`, drug chain | drug | Armoury |
| baradium | `KOTOR_Research_Baradium` only (explosives research) | research | Armoury |
| agrinium | `RSW_DW_Module_DroidArmorLte_agrinium` (droid armor module) | name only | ours |
| zersium | `guy762_brifle_zersium` (a rifle's name) | name only | Armoury |
| bacta | `RSW_Bacta`, patch, spray, tank | medicine | ours — **out of scope** (medicine, not a material) |
| duranium, doonium | none yet; registry rows `RSW_Duranium`, `RSW_Doonium` (RULED to exist) | — | to build |
| glass (becomes transparisteel, §3.8) | Stillsand chain: `RM_GlassSand`, `RM_FineSand`, `RM_SiftGlassSand` job + `RM_SandSieve`, `RM_SunGlass`, `RM_LensGlass`, `RM_MeltSunGlass`, `RM_MeltLensGlass`, `RM_SunFurnace`, `RM_LensBench`, `RM_PrecisionLens`, `RM_PearlLens`, `RSW_KraytLens`, `RM_SunGogglesGlass`; FlowWorks `RM_Make_Bottle_Glass` (stone blocks → `RM_BottleEmpty`) | glass | ours |

Not in the game anywhere (checked: 0 defs in `src/`; installed-mod sweep in §1b): phrik, transparisteel,
lommite, aurodium, chromium, quadanium, coaxium, impervium, thorilide, dolovite, corusca, carbonite,
hyperbaride, laminanium, ultrachrome, alusteel, neutronium, ferrocarbon.

The ship as exported (`The_Utinni.xml`) carries `VFEFactory_AutomatedSmelter` and no alloy forge. VFE
Factory's `VFEFactory_AutomatedAlloyForge` is in the live mod set (its `VFEFactory_AlloyPlasteel` makes
plasteel from steel, chemfuel and gold) but is not aboard. Fabrication routes that exist today are tabled in
`canon_metal_fabrication_2026-10-09.md` §1.

### 1a. Plasteel and durasteel as they stand in the game today (MEASURED)

Read from Core's `Items_Resource_Stuff.xml` and the Armoury's `Absorbed_KotorCore_KotORResource_Metals2.xml`:

| stat | steel (Core) | **plasteel** (Core) | **durasteel** (`KOTOR_AlloyDurasteel`) |
|---|---|---|---|
| mass per unit | 0.5 | **0.25** (half of steel) | **0.675** (heavier than steel) |
| market value | 1.9 | 9 | 5 |
| armor sharp / blunt / heat | 0.9 / 0.45 / 0.60 | **1.14** / 0.55 / 0.65 | 0.8 / **0.6** / **1.0** |
| hit points factor | 1 | 2.8 | **3** |
| work to make / build factor | 1 | **2.2** (slow to shape) | 1 |
| melee cooldown factor | — | **0.8** (fast, light weapons) | 1 |

So plasteel is the light, sharp-resistant, slow-to-work composite and durasteel the heavy, tough, heat- and
blunt-resistant structural alloy. The design keeps that split and gives each a canon job. `Mass` here is the
resource stack's weight and does not by itself make finished gear lighter or heavier, and the armor rows are
stuff armor powers, not final armor ratings. Durasteel's sharp power (0.8) sits below steel's, so "more
resistant than steel" holds only for blunt, heat and hit points until §3.2 raises it.

### 1b. Beyond `src/`

Canon materials from other active mods are Outer Rim - Core (beskar, pure beskar, durasteel, tibanna) and LK
mineables (beskar ore, durasteel ore). A sweep of every *installed* (incl. inactive) mod's Defs for the canon
names did not finish over the slow `/mnt/c` mount — **UNMEASURED** for inactive mods.

**Measured leak (2026-10-09):** Odyssey's own asteroid generation
(`Data/Odyssey/Defs/MapGeneration/SpaceMapGenerator.xml`, `GeneratedLocations.xml`) names `MineablePlasteel`,
`MineableGold`, `MineableSilver`, `MineableUranium`, `MineableJade` and `MineableComponentsIndustrial`. So
asteroid maps mine plasteel and components from rock, which the 2026-09-25 ruling forbids. Canon agrees:
plasteel is a manufactured material (§2a), not an ore.

## 2. Canon — what each material is for

Source: `starwars.fandom.com/api.php` `action=parse&prop=wikitext` on the **canon** page (not `/Legends`),
titles resolved with `list=search`, pulled 2026-10-09. Fabrication inputs and processes, per material, are in
`canon_metal_fabrication_2026-10-09.md` §3.

### 2a. Plasteel

`list=search&srsearch=plasteel` returns `Plasteel` (canon), `Plasteel/Legends`, `Drolan Plasteel` (Legends
company), `Impervium (plasteel)` (Legends brand), `Plasteel cutter`, `Plasteel cylinder`. Canon page facts,
each with the source Wookieepedia cites:

- "a hard material that had a variety of uses"; **interior doors** could be made of it — "The Perfect Weapon".
- Sidon Ithano's red **Kaleesh mask** — "The Crimson Corsair and the Lost Treasure of Count Dooku"; **parts of
  Darth Vader's helmet** — *Lords of the Sith*; Cardo (Knights of Ren) wore **plasteel-armored greaves**.
- **Treads**, e.g. the 125-Z treadspeeder — *The Rise of Skywalker: The Visual Dictionary*.
- **Reconstructive surgery**: a plasteel sleeve over a fused bone makes it as sturdy as the original; a
  plasteel mask over reshaped facial muscles — "The Face of Evil".
- **B1 battle droids** were constructed with plasteel — *Queen's Peril*.
- High strength, capable armor: **M3 Bulwark blast shields** of reinforced plasteel sheet shrug off blaster
  rifle fire and grenade shrapnel — *Rise of the Separatists*.
- Not stormtrooper armor: Ezra's "plasteel pigs" jibe is wrong in-universe; that armor is **plastoid** —
  *Star Wars Rebels: The Visual Guide*. Plasteel and plastoid are distinct canon materials.

Legends adds (flavour only, not canon): "combined acrylic polymers and metal alloys", keeping "the elastic
strength of plastics" with "the strength and heat resistance of metal"; yellows with age; droid casings;
construction droids extrude plasteel girders.

**Plasteel vs durasteel in canon:** durasteel is "a type of metal alloy" (canon page, type = Metal),
"more resistant than standard steel", "capable of protecting against kinetic damage", used for military
starship defensive plating, buildings, crates and stuncuffs, with **zersium** ore critical to making it.
Plasteel is a hard *composite* used where something must be shaped and carried: masks, helmet parts,
greaves, shields, droid bodies, treads, doors, bone sleeves. Canon never makes either a variant of the other.

### 2b. The other canon materials

| material | canon (sourced) | game role (one axis each) |
|---|---|---|
| **plasteel** | §2a | **Shape**: the light, formable composite (§3.1) |
| **durasteel** | galaxy-wide metal alloy: armor, buildings, crates, stuncuffs, military ship plating; zersium ore critical to making it | **Hold**: the heavy structural alloy (§3.1) |
| **beskar** | Mandalorian iron; withstands blaster fire and repels lightsabers; "found only on Mandalorian worlds"; reforged by Mandalorian smiths with a guarded method | apex personal armor; heirloom; used as found, reforged only by a Mandalorian armorer (§3.7) |
| **cortosis** | extremely rare; absorbs energy, can short out a lightsaber; brittle and porous in its natural state, useless as armor unalloyed; cortosis helmets hide thoughts from Force users | *anti-energy / anti-Force* — shields, dampers, psychic-hiding helmets; never bulk armor |
| **phrik** | rare robust alloy, lightsaber-resistant; mined on Gromas and on Tatooine (Mos Algo mine); electrostaffs; weaker than cortosis. Phrikite ore is Legends | *lightsaber-resistant WEAPONS*; trade and a rare desert deposit (§3.5) |
| **duranium** | tough military-grade plating, stronger than titanium; Grievous's armor, MagnaGuard frames | *heavy frames*: large machines, war droids, factory structures (owner: required) |
| **doonium** | heavy metal used primarily for starship construction; mined on planets and **asteroid fields**; with dolovite, shields the Death Star's hypermatter reactor core | *reactors and ship cores*; salvage, rare trade, asteroid ore (§3.5) |
| **transparisteel** | hardy transparent alloy for windows and canopies; can be blaster-proof; lommite ore is a major component | the game's only glass: windows, bottles, lenses, canopies, sifted from desert fine sand (§3.8) |
| **plastoid** | armor plastic (clone and stormtrooper armor), impervious to chemical warfare, vulnerable to blaster fire | *light sealed armor* — sealed suits, cheap mass armor |
| **aurodium** | yellow metal rarer than gold; currency standard, jewellery | *luxury / currency* metal; trade-only |
| **chromium** | rare valuable metal; royal Naboo ship plating; chromium–titanium alloy in hyperdrives | *plating / prestige finish*; trade-only |
| **quadanium** | Death Star hull plates, TIE wing frames | folds into durasteel; no def |
| **kyber** | Force-attuned living crystal; lightsabers; superweapon cores | *Force focus* (built: Lantern Deeps only) |
| **stygium** | crystals that power cloaking devices (TIE Phantom, Scimitar) | *ship and device cloaking*; trade-only |
| **tibanna** | reactive gas: hyperdrives, coolant, fuel, **supercharges blaster bolts** | *weapon gas / coolant*; beldon herds only (ruled 2026-09-12) |
| **coaxium** | hyperfuel, rare hypermatter; raw form explodes if not kept cold | *long-range gravship fuel*; trade-only |
| **rhydonium** | volatile starship fuel, explosive, toxic fumes, an addictive high | *dirty fuel* + drug (already modelled) |
| **zersium** | mineral ore essential to durasteel (canon only locale: Nag Ubdur) | the mineral that turns steel into durasteel (§3.2) |
| **lommite** | ore used to make transparisteel | no def: the desert's fine sand is the transparisteel feedstock (§3.8) |
| **carbonite**, **thorilide**, **dolovite**, **hyperbaride** | stasis; turbolaser shock absorbers; reactor shielding partner; Mimban mineral | no def until a consumer exists |
| **corusca gem** | extremely rare valuable gemstone | *luxury trade gem*; trade-only |
| **baradium** | volatile synthetic explosive | *explosives* (research exists) |
| **bronzium** | bronze-coloured decorative alloy | **dropped from the game** (§3.10) |

Not proposed: impervium (a Legends plasteel brand), laminanium, ultrachrome, alusteel, neutronium,
ferrocarbon, agrinium — stubs that only duplicate a role above.

### 2c. The three light/strong materials, kept apart

| | plastoid | plasteel | durasteel |
|---|---|---|---|
| what it is | armor plastic | hard composite | metal alloy |
| one verb | **Seal** | **Shape** | **Hold** |
| good at | cheap mass armor; sealed suits and helmets | strength per kilogram; sharp armor; formable into masks, shields, droid shells, implants | hit points, blunt and heat; walls, plating, vaults |
| bad at | blaster bolts | bulk (expensive, slow to work) | weight (worst of the three to carry) |
| canon tell | clone/stormtrooper armor | Vader's helmet parts, M3 blast shields, B1 droids | military ship plating, buildings |

## 3. The design

**Identity:** where a material comes from is what it is (provenance). **Main reward:** restoration —
damaged equipment and wrecks are the prize, and materials repair them. **Rare materials enter a build as
assemblies:** a large build or ancient-ship refit takes a durasteel shell, a plasteel housing, a duranium
frame and a doonium core, so all four have a job in the same machine without competing. (GPT review:
`design/RimMandrake/canon_materials_gpt_consult_2026-10-09.md`.)

The six origin channels: **L** local biome mining or gathering (via the registry), **S** salvage (wrecks,
Rust Cathedral, Warscar troves, crashed ships, B1 droid remains, Odyssey orbital debris and mech-ship chunks),
**A** asteroid mining (Odyssey space maps, reached by gravship), **T** offworld trade (Bazaar, orbital
traders), **H** herds/creatures, **F** fabrication aboard the ship (smelter or alloy forge). A gravship-gated
supply must never block the first gravship: every first-ship material has a ground salvage route.

### 3.1 Every material, its job and its source

| material | job (verb) | from | def |
|---|---|---|---|
| steel | baseline for everything | L (iron) | Core `Steel` |
| plasteel | **Shape** — armor plates, shields, helmets and masks, droid shells, prosthetics and implants, treads, light melee | S, T, F late (alloy forge, §3.4). Never L or A | Core `Plasteel` |
| durasteel | **Hold** — walls, blast doors, vaults, hull plating, heavy turret mounts, crates | S, T, F early (steel + zersium, §3.2) | `RSW_Durasteel` (new) |
| plastoid | **Seal** — sealed suits and helmets, cheap mass armor | S (Imperial), F from chemfuel | `KOTOR_Plastoid` |
| duranium | **Brace** — frames of large ships and machines (owner: required) | S, rare T | `RSW_Duranium` (registry row) |
| doonium | **Contain** — reactor cores, gravship core/engines, radiation shielding (owner: required for large ones) | S, rare T, A ore smelted aboard with glower crust (§3.5) | `RSW_Doonium` (registry row) |
| beskar | **Protect** — apex personal armor; heirloom | S only; reforged only by the Mandalorian armorer (§3.7) | existing Armoury / Outer Rim defs |
| cortosis | **Disrupt** — energy absorption: shields, Force-dampening helmets, saber-shorting weave | S, T | `KOTOR_IngotCortosis` |
| kyber | **Focus** — lightsabers, superweapon cores | L Lantern Deeps only | built |
| tibanna | **Charge** — blaster supercharge, coolant | H beldons only | one def (§3.10) |
| rhydonium | dirty fuel + drug | as modelled today | built |
| phrik | **Parry** — lightsaber-resistant staffs and blades | T, L rare desert phrikite smelted aboard (§3.5) | `RSW_Phrik` (new) |
| transparisteel | **Observe** — windows, canopies, domes, bottles, lenses: all glass | L+F sifted desert fine sand (§3.8), T | `RSW_Transparisteel` (new) |
| stygium | **Conceal** — ship and device cloaking | T only | `RSW_Stygium` (new) |
| coaxium | **Extend** — gravship range; volatile, must be kept cold | T only | `RSW_Coaxium` (new) |
| aurodium, corusca, chromium | wealth and trade value | T only | no def until a consumer exists |

Folded or deferred: quadanium, alusteel and ferrocarbon fold into durasteel's function; carbonite,
thorilide, dolovite and hyperbaride get no def until something consumes them; name-only `agrinium` is not
promoted to a material. Bronzium is removed (§3.10).

### 3.2 Durasteel: one def, donors convert in, made from steel + zersium

`RSW_Durasteel` is canon Star Wars, so it sits in the RimStarWars tier (`RSW_`, packageId `mandrake.rsw.*`)
per `design/NAMING_SCHEME_PLAN.md`. Starting stats: `KOTOR_AlloyDurasteel`'s (§1a), with its sharp armor power
raised to steel's (0.9) so "more resistant than standard steel" holds on every axis it is worn on.

| donor def | what happens |
|---|---|
| `KOTOR_AlloyDurasteel` (Armoury, ours) | stops being produced; its slag, smelt and ship-chunk recipes yield `RSW_Durasteel`; loose stacks convert 1:1 |
| `KotORChunk_durasteel`, `ShipChunk_durasteel` | smelt/deconstruct yields point at `RSW_Durasteel` (salvage re-melt aboard) |
| `OuterRim_Durasteel` | conversion recipe 1:1; its mining and deep-drill producers zeroed; recipes that consume it redirected |
| `LKDurasteel_Ore` | its mining and deep-drill producers zeroed; existing stacks convert at a yield set after measuring what the def is |
| `KOTOR_MineableDurasteel` | stops generating; kept loadable for saves |
| `kotor_IngotDurasteel_recipe` (+10×; steel + uranium) | removed: uranium is not a canon input; the steel + zersium route replaces it |

**Fabrication — proposed, TO CONFIRM:** steel + **zersium** → `RSW_Durasteel` on the ship's smelter
(`VFEFactory_AutomatedSmelter`), available early. If the owner prefers it on the alloy forge instead, it is
that forge's first recipe (§3.4); either way it is the early alloy. Zersium is a new mineral def,
`RSW_Zersium`, with no local mineral today: **its source is TO CONFIRM** (canon names one bedrock world, Nag
Ubdur; candidates are an asteroid ore beside doonium, or a rare deep deposit placed through the registry).

Migration: loose-stack conversion does not migrate built walls, worn gear, bills or saved filters, so each
donor def stays loadable until the save that carries it is replaced.

### 3.3 Plasteel: salvage, trade, and late fabrication

Plasteel keeps Core's `Plasteel` def, label and stats (§1a). Its routes:

- **Salvage and re-melt (from the start):** ship chunks and `KotORChunk_plasteel` slag re-melt to plasteel
  aboard. A ship chunk can honestly yield durasteel plating, plasteel shells and components together; B1
  remains give plasteel once, not again through corpse processing and a wreck recipe.
- **Trade.**
- **Alloy forge, late (§3.4):** one plasteel recipe, behind the forge's later research.
- **Removed:** every other recipe that makes plasteel — `Make_PlasteelGF` (GravForge), `kotor_Plasteel_recipe`
  (+10×; plastoid + steel at the plasma furnace), and Rimefeller's `UncuredPlasteel` if it proves to be a
  route. Odyssey's `MineablePlasteel` and `MineableComponentsIndustrial` asteroid scatter is patched out of
  both measured generation paths with an explicit allowlist, not only zeroed commonality.

### 3.4 The alloy forge

The ship needs an alloy forge, possibly early, whose recipes unlock progressively: easier alloys first,
harder ones later. Order: **durasteel early** (if it is not on the smelter, §3.2), **plasteel late**. The
building: VFE Factory's `VFEFactory_AutomatedAlloyForge` is in the live mod set and ship tooling already names
it (`src/RimMandrake/Utils/rimbench/shipbuild.py`); its stock `VFEFactory_AlloyPlasteel` (steel + chemfuel +
gold) is the plasteel recipe to keep or retune, gated behind a late research. It goes aboard the ship (the
deck plan's Wing E, `design/Jawa/worldbuilding/ship_deck_plan.md`). Exotic metals (duranium, beskar,
cortosis) are never forged here.

### 3.5 Asteroid and desert ores smelted aboard: doonium and phrik

- **Doonium** — salvage, rare trade, **and** doonium ore on Odyssey asteroid maps (canon: mined on asteroid
  fields), smelted aboard. **Glower crust is an ingredient** of the smelt: doonium ore + `RM_GlowerCrust` →
  `RSW_Doonium`. That is mostly lore, but it connects them, and it is what gives glower crust its trade value
  (traders buy it as doonium feedstock). New def: a doonium ore mineable for asteroid maps only, never on the
  planet surface; amounts in the registry.
- **Phrik** — trade **and** a rare desert phrikite deposit (canon: phrik mined on desert Tatooine), smelted
  aboard into `RSW_Phrik`. New def: a phrikite mineable placed in one desert biome through the registry.

### 3.6 Trade-only goods

`RSW_Stygium` and `RSW_Coaxium` are defined now as trade goods: labelled, described from canon (§2b),
valued, stocked by orbital traders and the Bazaar at low frequency, with no local, salvage, asteroid or
recipe source. Stygium already exists as donor items (`KOTOR_StygiumCrystal`, `guy762_crystalitem_stygium`);
those convert into `RSW_Stygium` and stop being produced. Stygium alone cloaks ships. Coaxium's description
carries its canon hazard (explodes unless kept cold); the mechanic waits for its consumer. `RSW_Phrik` and
`RSW_Transparisteel` are also stocked by the same traders, beside their local routes (§3.5, §3.8).

### 3.7 Beskar: used as found; only the Mandalorian armorer reforges it

- Beskar pieces (ingots, armour, relics) are **salvage only**, and the colony uses them as found.
- **The colony can never reforge beskar.** Smelting beskar, or anything made of it, **destroys it**: it comes
  out as lesser ores (steel and slag), never beskar. That covers the Armoury's `kotor_IngotBeskar_recipe`
  (+10×), which turns raw beskar into ingots and is removed, and vanilla smelting of beskar apparel and
  weapons, which would otherwise return beskar.
- **Only a rare Mandalorian armorer can reforge it**, reached through a quest with the Blackstar Company
  (`design/Jawa/worldbuilding/FACTION_SPEC.md` entry 10). Reforging takes the player's beskar pieces and
  returns them as new beskar gear. The quest design is owed and needs the owner (`BESKAR_ARMORER_QUEST_1`).
- Beskar mining routes (`KOTOR_MineableBeskar`, `OuterRim_Beskar`, `LKBeskar_Ore`) produce nothing.

### 3.8 Transparisteel replaces glass

Transparisteel is what the extreme desert's fine sand is sifted and filtered into, and it is the game's
**only** glass: every glass bottle, glass object and lens is transparisteel. What exists today (§1) maps
onto it:

- **Feedstock:** `RM_FineSand` (sifted from `RM_GlassSand` by the built `RM_SiftGlassSand` job and
  `RM_SandSieve`) is the transparisteel feedstock. The Stillsand is the extreme desert
  (`BiomeWorker_ExtremeDesert`). No lommite def.
- **Material:** `RM_SunGlass` and `RM_LensGlass` fold into one `RSW_Transparisteel`, made from fine sand at
  the sun furnace. The two `Melt…` recipes become one.
- **Objects:** glass bottles (`RM_Make_Bottle_Glass`, today melted from stone blocks) are made from
  transparisteel; precision, pearl and krayt lenses and sun-goggle glass are ground from transparisteel.
- **Tier:** transparisteel is a canon name, so per `biome_mod_architecture.md` §7 Q11a the campaign gets it
  through the Star Wars layer; the franchise-free Stillsand chain may keep a generic glass of its own, which
  the campaign never produces.
- **Natural glasses stay what they are.** Found or grown materials that are not made at a bench (biosilica,
  glass pearl, waveglass, fexxil glass, aurora glass, fulgurite, lanternstone, floatstone, veil pane) keep
  their own defs and biome jobs; they are not a second glass tier. Built in `GLASS_TO_TRANSPARISTEEL_1`.

### 3.9 Our own materials beside the canon ones

- `RM_CloakLacquer` is **personal camouflage** (cloaks a pawn); it never cloaks a ship or device.
- `RUT_Mindstone` is the **droid-mind crystal**: the Focus crystal for machines, where kyber is the Focus for
  the Force.
- `RSW_Leather_KraytDragon` is an **ordinary top leather**: best of the hides, not beskar-class, no heirloom
  or quest rule.
- `RM_GlowerCrust` keeps its built uses (glower plate, shield panel, dirty fuel) and is a doonium ingredient
  (§3.5).

### 3.10 Removals and merges

- **Bronzium is dropped from the game:** `KOTOR_AlloyBronzium`, `KOTOR_MineableBronzium`,
  `KotORChunk_bronzium` and its slag recipe, the junk-pile `mineableThing` that yields it, and the bronzium
  light battle armor. Placed bronzium things (4 on the exported ship) are re-stuffed.
- **One chitin ladder:** the three stat-identical copies (Lantern Deeps `RM_*Chitin`, the Rot `RM_Rot*Chitin`,
  Bestiary `RSW_*Chitin`) fold into one set, and every producer points at it.
- **The 7 `RUT_` duplicates of `RM_` items are dropped:** `RUT_GlowerCrust`, `RUT_CathedralRoachShell`,
  `RUT_BrinePlate`, `RUT_SeepStone`, `RUT_SaltCameo`, `RUT_Hardwood`, `RUT_SweetlineWool`. Producers and C#
  references point at the `RM_` def (for the hardwood pair, `RUT_Hardwood` is the code-referenced one, so the
  code moves first).
- **One common salt**, with the four Grey Sea crystal salts (`RM_SaltWhite`, `RM_SaltPink`, `RM_SaltViolet`,
  `RM_SaltAmber`) kept as the premium curing set. The other coarse salts (raw, delta, seep, kettlewick, brine,
  brine plates) become biome sources of the one common salt.
- **Plasteel slag:** `ChunkSlagPlasteel_GT` folds into `KotORChunk_plasteel`.
- **Tibanna:** `KOTOR_Tibanna` and `RUT_TibannaGas` become one def; beldon herds are the only source and the
  pipe network is a consumer.

Every removal is save-checked first (§5). Built in `MATERIAL_MERGES_CLEANUP_1`.

## 4. Material jobs: preferences, key jobs held

**Everywhere** a job accepts a broad material category, any eligible material works and the wrong one just
costs the player — weaker, heavier, slower or pricier, as the layout page grades it. Nothing is refused.

**Key jobs are held as preferences.** The six below name each job's right material; it gives the best
result there, and every other eligible material still works. None of them is enforced through a fixed
ingredient list.

| key job | right material | why |
|---|---|---|
| ship hull plating | durasteel | canon military ship plating; the gravship and ancient-hull skin |
| blast doors and vault doors | durasteel | the canon blast door |
| droid shells | plasteel | canon B1 bodies; the droid repair loop runs on it |
| prosthetics and implants | plasteel | canon bone sleeves and masks; light and body-safe |
| large frames (large ships, machines, factories) | duranium | owner rule 2026-10-03: REQUIRED |
| reactor and ship cores | doonium | owner rule 2026-10-03: REQUIRED |

The two "REQUIRED" rows are the owner's 2026-10-03 rule for large ship and machine types, which this hold does
not change. Single-material jobs (ship cloaking needs stygium, lightsaber foci need kyber, range needs
coaxium) are not on the list because nothing else could do them in the first place.

## 5. Save migration (applies to every removal and fold)

The world is remade at the end, so only what the remake carries — the gravship, its cargo and the founders —
must survive a def change. For each removed or folded defName: check the canonical start save and the
exported ship (`The_Utinni.xml`) for it with the savegame tooling (`rimworld-savegame` skill; grep `<def>NAME</def>`,
not the bare name); where it is present, map it to the surviving def (a back-compat defName mapping, or the
old def kept loadable and unproduced) rather than letting the load drop the thing.

## 6. Build duties

`CANON_MATERIALS_BUILD_1` (the core):

1. `RSW_Durasteel` and the donor conversion of §3.2, with both recipe audits: fixed `Plasteel` costs stay
   where the consumer needs plasteel; only identified durasteel references are redirected; broad ingredient
   filters that admit both are checked separately.
2. Plasteel: remove every crafting route but the alloy forge's (§3.3); patch Odyssey's asteroid generation.
3. Salvage yields by composition for durasteel, plasteel, duranium and doonium; re-melt of durasteel and
   plasteel salvage aboard.
4. `RSW_Duranium`, `RSW_Doonium`, `RSW_Phrik`, `RSW_Transparisteel`, `RSW_Stygium`, `RSW_Coaxium` defs, trader
   and Bazaar stock, stygium donor conversion.
5. Beskar self-reforging removed and beskar smelting made destructive (§3.7).
6. The §3.9 roles written into the defs' descriptions.

Split items, filed for FOUNDRY:

- `SHIP_ALLOY_FORGE_1` — the alloy forge aboard, progressive unlocks, the plasteel recipe, the durasteel
  steel + zersium route and `RSW_Zersium` (route and source TO CONFIRM, §3.2, §3.4).
- `ASTEROID_DESERT_ORES_1` — doonium asteroid ore with the glower-crust smelt, and the desert phrikite
  deposit, both smelted aboard (§3.5).
- `GLASS_TO_TRANSPARISTEEL_1` — §3.8.
- `MATERIAL_MERGES_CLEANUP_1` — §3.10 with §5.
- `BESKAR_ARMORER_QUEST_1` — the Blackstar quest to the Mandalorian armorer (§3.7); needs the owner.
