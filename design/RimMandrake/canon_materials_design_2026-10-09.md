# CANON_MATERIALS_DESIGN_1 — canon Star Wars materials: what they are for and where they come from

2026-10-09. **Decided design**, built under `CANON_MATERIALS_BUILD_1`. One part is still a proposal: the
key-job list in §4, which the owner confirms before it is enforced.
The jobs × materials layout is `Transient/canon_materials_jobs_layout_2026-10-09.html`.
Placement numbers live in `design/RimMandrake/mineral_abundance_registry_2026-10-03.csv`; this doc decides
*roles* and *channels*, the registry carries the amounts.

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
- Decisions taken by question card 2026-10-09:
  - durasteel is a new def of ours, `RSW_Durasteel`, and every donor durasteel converts into it (§3.2);
  - material jobs are **preferences** (soft penalties) everywhere except a few **key jobs**, which are
    exclusive (§4);
  - plasteel comes from salvage and trade only, and is never craftable;
  - durasteel comes from salvage and trade only; there is no local zersium ore or alloy recipe;
  - phrik, transparisteel, stygium and coaxium get their defs now, as trade-only goods (§3.4).
- Owner typed 2026-10-09: *"I've ruled this before. All three will exist. Duranium and Doonium are mostly
  salvage and possibly rare trade."* (2026-10-03 typed: both made offworld, pretty rare, REQUIRED to build
  large ship and machine types such as factories.)
- 2026-10-03 and 2026-10-09 (cards): precious metals and gems only in their home biomes; deep drilling = iron
  everywhere, everything else by home biome.
- 2026-09-25 typed: components and plasteel are never mined from rock; salvage is a major source of advanced
  materials.

## 0a. The governing loop

Materials in this game serve **recovery, refit and repair**, plus the **occasional hack** that needs a rare
material:

- **Salvage routes, not planet mining.** The planet does not hold every interesting mineral. Local mines give
  the basics (iron for steel, a few home-biome ores, Lantern Deeps kyber); the advanced materials are pulled
  from wrecks.
- **Trade-only materials tie the colony to the galaxy.** Seven never appear on the planet: coaxium, aurodium,
  corusca, chromium, phrik, transparisteel and stygium. The only way to get them is a trader or the Bazaar.
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
(26,589 ThingDefs from the live-set def dump, 73 mineral materials). `S` = has `stuffProps`.

| material | defs that carry it today | form today | owner |
|---|---|---|---|
| plasteel | Core `Plasteel` (S, `Metallic`); KotOR smelt/slag recipes; crashed shuttles and `ShipChunk_durasteel` yield it | Core stuff | Core |
| durasteel | `KOTOR_AlloyDurasteel` (S), `KOTOR_MineableDurasteel`, `KotORChunk_durasteel` slag + smelt recipes, `ShipChunk_durasteel`, powered durasteel walls; `OuterRim_Durasteel`; `LKDurasteel_Ore` | alloy + ore | Armoury (ours), Outer Rim, LK |
| beskar / Mandalorian iron | `KOTOR_RawBeskar`, `KOTOR_IngotBeskar` (S), `KOTOR_MineableBeskar`; Outer Rim `OuterRim_Beskar`, `OuterRim_PureBeskar` (+ floors); LK `LKBeskar_Ore` | ore + ingot + stuff | Armoury, Outer Rim, LK |
| cortosis | `KOTOR_IngotCortosis` (S), `KOTOR_MineableCortosis`, `guy762_armband_cortosis` | ingot | Armoury |
| bronzium | `KOTOR_AlloyBronzium` (S), `KOTOR_MineableBronzium`, slag, bronzium light battle armor | alloy | Armoury |
| plastoid | `KOTOR_Plastoid` (S), smelt recipes | stuff | Armoury |
| kyber | `Force_KyberCrystal`, `Force_CrystalFormation_*` (Lantern Deeps scatter `RUT_LanternDeepKyberScatter`), synthetic/bled/cleansed crystals, kyber quests | crystal | SW The Force, ours |
| stygium | `KOTOR_StygiumCrystal`, `guy762_crystalitem_stygium`, stygium cloaking research | crystal | Armoury |
| tibanna | `KOTOR_Tibanna` + pipe net, `RUT_TibannaGas`, `OuterRim_Tibanna` | gas / item | Armoury, ours (beldon herds, the Forge) |
| rhydonium | `KOTOR_RawRhydonium`, `KOTOR_Rhydonium` fuel, rhydonium reactors, drug chain | fuel + drug | Armoury |
| spice | `KOTOR_Spice`, `KOTOR_MineableSpice`, drug chain | drug | Armoury |
| baradium | `KOTOR_Research_Baradium` only (explosives research) | research | Armoury |
| agrinium | `RSW_DW_Module_DroidArmorLte_agrinium` (droid armor module) | name only | ours |
| zersium | `guy762_brifle_zersium` (a rifle's name) | name only | Armoury |
| bacta | `RSW_Bacta`, patch, spray, tank | medicine | ours — **out of scope** (medicine, not a material) |
| duranium, doonium | none yet; registry rows `RSW_Duranium`, `RSW_Doonium` (RULED to exist) | — | to build |

Not in the game anywhere (checked: 0 defs in `src/`; installed-mod sweep in §1a): phrik, transparisteel,
lommite, aurodium, chromium, quadanium, coaxium, impervium, thorilide, dolovite, corusca, carbonite,
hyperbaride, laminanium, ultrachrome, alusteel, neutronium, ferrocarbon.

### 1a. Plasteel and durasteel as they stand in the game today (MEASURED)

Read from Core's `Items_Resource_Stuff.xml` and the Armoury's `Absorbed_KotorCore_KotORResource_Metals2.xml`.
The two are already on different axes, which is what the redo builds on:

| stat | steel (Core) | **plasteel** (Core) | **durasteel** (`KOTOR_AlloyDurasteel`) |
|---|---|---|---|
| mass per unit | 0.5 | **0.25** (half of steel) | **0.675** (heavier than steel) |
| market value | 1.9 | 9 | 5 |
| armor sharp / blunt / heat | 0.9 / 0.45 / 0.60 | **1.14** / 0.55 / 0.65 | 0.8 / **0.6** / **1.0** |
| hit points factor | 1 | 2.8 | **3** |
| work to make / build factor | 1 | **2.2** (slow to shape) | 1 |
| melee cooldown factor | — | **0.8** (fast, light weapons) | 1 |

So plasteel is the light, sharp-resistant, slow-to-work composite and durasteel the heavy, tough, heat- and
blunt-resistant structural alloy. The design keeps that split and gives each a canon job. Two caveats: `Mass`
here is the resource stack's weight and does not by itself make finished gear lighter or heavier (dedicated
gear needs its own masses), and the armor rows are stuff armor powers, not final armor ratings. Durasteel's
sharp power (0.8) sits below steel's, so "more resistant than steel" holds only for blunt, heat and hit points.

### 1b. Beyond `src/`

Canon materials from other active mods are Outer Rim - Core (beskar, pure beskar, durasteel, tibanna) and LK
mineables (beskar ore, durasteel ore). A sweep of every *installed* (incl. inactive) mod's Defs for the canon
names did not finish over the slow `/mnt/c` mount — **UNMEASURED** for inactive mods.

**Measured leak (2026-10-09):** Odyssey's own asteroid generation
(`Data/Odyssey/Defs/MapGeneration/SpaceMapGenerator.xml`, `GeneratedLocations.xml`) names `MineablePlasteel`,
`MineableGold`, `MineableSilver`, `MineableUranium`, `MineableJade` and `MineableComponentsIndustrial`. So
asteroid maps mine plasteel and components from rock, which the 2026-09-25 ruling forbids, unless the
minerals work patches it. Canon agrees with the ruling: plasteel is a manufactured composite (§2), not an ore.

## 2. Canon — what each material is for

Source: `starwars.fandom.com/api.php` `action=parse&prop=wikitext` on the **canon** page (not `/Legends`),
titles resolved with `list=search`, pulled 2026-10-09. One line of canon use, then the material's ROLE
in this game (§3).

### 2a. Plasteel (re-pulled 2026-10-09 for this redo)

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
strength of plastics" with "the strength and heat resistance of metal"; used in armor, ship components,
containers and construction; yellows with age (*Darth Maul: Shadow Hunter*); droid casings (MI-series
security droid, Scarab Mark VI); construction droids extrude plasteel girders (*The Essential Guide to
Droids*); military grade as light as polythin (*Wretched Hives of Scum & Villainy*).

**Plasteel vs durasteel in canon:** durasteel is "a type of metal alloy" (canon page, type = Metal),
"more resistant than standard steel", "capable of protecting against kinetic damage", used for military
starship defensive plating, buildings, crates and stuncuffs, with **zersium** ore critical to making it.
Plasteel is a hard *composite* used where something must be shaped and carried: masks, helmet parts,
greaves, shields, droid bodies, treads, doors, bone sleeves. Canon never makes either a variant of the other.

### 2b. The other canon materials

| material | canon (sourced) | proposed game role (one axis each) |
|---|---|---|
| **plasteel** | §2a: masks, helmet parts, greaves, blast shields, droid bodies, treads, doors, surgical bone sleeves | **Shape**: the light, formable composite — personal armor plates and shields, droid shells, prosthetics and implants, treads, light weapons. Salvage and trade only |
| **durasteel** | galaxy-wide metal alloy: armor, buildings, crates, stuncuffs, military ship plating; "more resistant than standard steel", kinetic protection; zersium ore critical to making it | **Hold**: the heavy structural alloy — walls, blast doors, hull plating, vaults, heavy turrets, crates. High HP, heavy, cheap to work. Salvage and trade only |
| **beskar** | Mandalorian iron; armor that withstands blaster fire and repels lightsabers; "found only on Mandalorian worlds"; reforgeable; making weapons of it taboo to the Children of the Watch | apex *personal armor*; heirloom; never mass-produced |
| **cortosis** | extremely rare; absorbs energy (dissipates blaster bolts), can short out a lightsaber; **brittle and porous in its natural state**, useless as armor unalloyed; cortosis helmets hide the wearer's thoughts from Force users | *anti-energy / anti-Force* — shields, dampers, psychic-hiding helmets; never bulk armor |
| **phrik** | rare robust alloy, lightsaber-resistant; mined on Gromas and Tatooine (Mos Algo mine); electrostaffs, Sidious's lightsabers; weaker than cortosis | *lightsaber-resistant WEAPONS* (staffs, blades) — the weapon twin of beskar's armor. Trade-only here |
| **duranium** | tough military-grade plating, stronger than titanium, less resilient than impervium; Grievous's armor, MagnaGuard frames | *heavy frames*: large machines, war droids, factory structures (owner: required for large ship/machine types) |
| **doonium** | heavy metal used primarily for **starship construction**; Empire stockpiled it for the Death Star, essential (with dolovite) in **shielding the hypermatter reactor core**; mined on many planets and asteroid fields | *reactors and ship cores* — power plants, gravship engines/cores, radiation shielding |
| **transparisteel** | hardy transparent alloy for windows and canopies; can be blaster-proof; lommite ore is a major component | *see-through strong wall/window*; cockpit canopies. Trade-only here (no lommite) |
| **plastoid** | armor plastic (clone and stormtrooper armor), impervious to chemical warfare, vulnerable to blaster fire | *light sealed armor* — sealed suits (tox/gas), cheap mass armor |
| **bronzium** | bronze-coloured alloy for statues, decorative finishes, some armor | *art and furniture beauty*, cheap decorative alloy |
| **aurodium** | yellow metal rarer than gold; currency standard (Cantonica), jewellery, a lightsaber hilt | *luxury / currency* metal (the galaxy's gold); trade-only |
| **chromium** | rare valuable metal; royal Naboo ship plating; reflects some radiation; chromium–titanium alloy needed in hyperdrives | *plating / prestige finish*; trade-only |
| **quadanium** | metallic substance for ships and battle stations (Death Star hull plates, TIE wing frames), turbolasers, shields | folds into durasteel; no def |
| **kyber** | Force-attuned living crystal; lightsabers; large ones at the heart of superweapons | *Force/energy focus* (already ours: Lantern Deeps only) |
| **stygium** | crystals that power cloaking devices (TIE Phantom, Scimitar) | *stealth*. Trade-only |
| **tibanna** | reactive gas: hyperdrives, repulsorlift coolant, fuel, **supercharges blaster bolts** | *weapon gas / coolant* (RULED: beldon herds) |
| **coaxium** | hyperfuel, rare hypermatter, mined on Kessel; raw form unstable and explodes if not kept cold | *long-range gravship fuel*; volatile cargo. Trade-only |
| **rhydonium** | volatile starship fuel, explosive, toxic fumes, an addictive high | *dirty fuel* + drug (already modelled) |
| **carbonite** | carbon-freezing: preserves goods and people; used to transport tibanna and coaxium | *stasis / preservation*; no def until a consumer exists |
| **thorilide** | prized crystal for turbolaser shock absorbers, mined with baradium | no def until a consumer exists |
| **zersium** | mineral ore essential to durasteel | none: durasteel is not made locally, so no zersium def |
| **lommite** | ore used to make transparisteel; scattered surface deposits on a desert planetoid | none: transparisteel is trade-only |
| **dolovite** | mined on the lava worlds Mustafar and Samovar; with doonium shields reactor cores | no def until a consumer exists |
| **corusca gem** | extremely rare valuable gemstone; smuggler's cargo | *luxury trade gem*; trade-only |
| **hyperbaride** | valuable mineral on Mimban (a mud world) | no def until a consumer exists |
| **baradium** | volatile synthetic explosive: thermal detonators, mining charges | *explosives* (research exists) |

Not proposed: impervium (a Legends plasteel brand; no canon role), laminanium, ultrachrome, alusteel,
neutronium, ferrocarbon, agrinium — stubs of one or two sentences that only duplicate a role above.

### 2c. The three light/strong materials, kept apart

Plastoid, plasteel and durasteel are the three a player meets first, and canon separates them cleanly:

| | plastoid | plasteel | durasteel |
|---|---|---|---|
| what it is | armor plastic | hard composite ("polymer + metal" is Legends; canon says only "hard material") | metal alloy |
| one verb | **Seal** | **Shape** | **Hold** |
| good at | cheap mass armor; sealed suits and helmets (the suit, not the plate, gives gas/toxin protection) | strength per kilogram; sharp armor; formable into masks, shields, droid shells, implants | hit points, blunt and heat; walls, plating, vaults |
| bad at | blaster bolts | bulk (expensive, slow to work) | weight (worst of the three to carry) |
| canon tell | clone/stormtrooper armor | Vader's helmet parts, M3 blast shields, B1 droids | military ship plating, buildings |

## 3. The design

**Identity:** where a material comes from is what it is (provenance). **Main reward:** restoration —
damaged equipment and wrecks are the prize, and materials repair them. **Rare materials enter a build as
assemblies:** a large build or ancient-ship refit takes a durasteel shell, a plasteel housing, a duranium
frame and a doonium core, so all four have a job in the same machine without competing. (GPT review,
gpt-6.1-sol high effort: `design/RimMandrake/canon_materials_gpt_consult_2026-10-09.md`; its corrections are
folded in below.)

The six origin channels: **L** local biome mining (via the registry), **S** salvage (wrecks, Rust Cathedral,
Warscar troves, crashed ships, B1 droid remains, Odyssey orbital debris and mech-ship chunks), **A** asteroid
mining (Odyssey space maps, reached by gravship), **T** offworld trade (Bazaar, orbital traders), **H**
herds/creatures, **F** fabrication at a bench. A gravship-gated supply must never block the first gravship:
every first-ship material has a ground salvage route.

### 3.1 Every material, its job and its source

| material | job (verb) | from | def |
|---|---|---|---|
| steel | baseline for everything | L (iron) | Core `Steel` |
| plasteel | **Shape** — armor plates, shields, helmets and masks, droid shells, prosthetics and implants, treads, light melee | S, T. Never L, A or F | Core `Plasteel` |
| durasteel | **Hold** — walls, blast doors, vaults, hull plating, heavy turret mounts, crates | S, T. Never L or F | `RSW_Durasteel` (new, §3.2) |
| plastoid | **Seal** — sealed suits and helmets, cheap mass armor | S (Imperial), F from chemfuel/neutroamine | `KOTOR_Plastoid` |
| duranium | **Brace** — frames of large ships and machines (owner: required) | S, rare T | `RSW_Duranium` (registry row) |
| doonium | **Contain** — reactor cores, gravship core/engines, radiation shielding (owner: required for large ones) | S, rare T | `RSW_Doonium` (registry row) |
| beskar | **Protect** — apex personal armor; reforgeable heirloom | S only | existing Armoury / Outer Rim defs |
| cortosis | **Disrupt** — energy absorption: shields, Force-dampening helmets, saber-shorting weave | S, T | `KOTOR_IngotCortosis` |
| bronzium | **Decorate** — statues, furniture, finishes | F alloy, T | `KOTOR_AlloyBronzium` |
| kyber | **Focus** — lightsabers, superweapon cores | L Lantern Deeps only | built |
| tibanna | **Charge** — blaster supercharge, coolant | H beldons | built |
| rhydonium | dirty fuel + drug | as modelled today | built |
| phrik | **Parry** — lightsaber-resistant staffs and blades | T only | `RSW_Phrik` (new, §3.4) |
| transparisteel | **Observe** — windows, canopies, observation domes | T only | `RSW_Transparisteel` (new, §3.4) |
| stygium | **Conceal** — cloaking | T only | `RSW_Stygium` (new, §3.4) |
| coaxium | **Extend** — gravship range; volatile, must be kept cold | T only | `RSW_Coaxium` (new, §3.4) |
| aurodium, corusca, chromium | wealth and trade value | T only | no def until a consumer exists |

Folded or deferred: quadanium, alusteel and ferrocarbon fold into durasteel's function; carbonite,
thorilide, dolovite and hyperbaride get no def until something consumes them; name-only `agrinium` and
`zersium` items are not promoted to materials.

### 3.2 Durasteel: one def, donors convert in

`RSW_Durasteel` is canon Star Wars, so it sits in the RimStarWars tier (`RSW_`, packageId `mandrake.rsw.*`)
per `design/NAMING_SCHEME_PLAN.md`. Starting stats: `KOTOR_AlloyDurasteel`'s (§1a — heavy, high HP, blunt-
and heat-resistant), with its sharp armor power raised to steel's (0.9) so "more resistant than standard
steel" holds on every axis it is worn on.

| donor def | what happens |
|---|---|
| `KOTOR_AlloyDurasteel` (Armoury, ours) | stops being produced; its slag, smelt and ship-chunk recipes yield `RSW_Durasteel`; loose stacks convert 1:1 |
| `KotORChunk_durasteel`, `ShipChunk_durasteel` | smelt/deconstruct yields point at `RSW_Durasteel` |
| `OuterRim_Durasteel` | conversion recipe 1:1; its mining and deep-drill producers zeroed; recipes that consume it redirected |
| `LKDurasteel_Ore` | its mining and deep-drill producers zeroed; existing stacks convert at a yield set after measuring what the def is |
| `KOTOR_MineableDurasteel` | stops generating; kept loadable for saves |

Migration: loose-stack conversion does not migrate built walls, worn gear, bills or saved filters, so each
donor def stays loadable (with a compatibility def shipped once its mod is retired) until the save that
carries it is replaced.

### 3.3 Plasteel: salvage and trade only

Plasteel keeps Core's `Plasteel` def, label and stats (§1a). Every route that makes it from anything else is
removed: no bench recipe, no smelt-from-ore, no rock source. Odyssey's `MineablePlasteel` (and
`MineableComponentsIndustrial`) asteroid scatter is patched out of both measured generation paths with an
explicit allowlist, not only zeroed commonality. Salvage yields by composition: a ship chunk can honestly
yield durasteel plating, plasteel shells and components together; B1 remains give plasteel once, not again
through corpse processing and a wreck recipe.

### 3.4 Trade-only goods reserved now

`RSW_Phrik`, `RSW_Transparisteel`, `RSW_Stygium` and `RSW_Coaxium` are defined now, as trade goods:
labelled, described from canon (§2b), valued, stocked by orbital traders and the Bazaar at low frequency, and
given no local, salvage, asteroid or recipe source. Stygium already exists as donor items
(`KOTOR_StygiumCrystal`, `guy762_crystalitem_stygium`); like durasteel, those convert into `RSW_Stygium` and
stop being produced. Consumers (cloaking, phrik weapons, windows, gravship range) are built with their
features; until then the goods are trade value. Coaxium's description carries its canon hazard (explodes
unless kept cold); the mechanic waits for its consumer.

## 4. Material jobs: preferences, with a few key jobs exclusive

**Everywhere** a job accepts a broad material category, any eligible material works and the wrong one just
costs the player — weaker, heavier, slower or pricier, as the layout page grades it. Nothing is refused.

**Key jobs** take only their material. PROPOSED, for the owner's confirmation before it is enforced:

| key job | only material | why it is obvious |
|---|---|---|
| ship hull plating | durasteel | canon military ship plating; the gravship and ancient-hull skin |
| blast doors and vault doors | durasteel | the canon blast door; a vault of anything else is not a vault |
| droid shells | plasteel | canon B1 bodies; the droid repair loop runs on it |
| prosthetics and implants | plasteel | canon bone sleeves and masks; light and body-safe |
| large frames (large ships, machines, factories) | duranium | owner rule 2026-10-03: REQUIRED |
| reactor and ship cores | doonium | owner rule 2026-10-03: REQUIRED |

Single-material jobs (cloaking needs stygium, lightsaber foci need kyber, range needs coaxium) are not on the
list because nothing else could do them in the first place.

Exclusivity is enforced through fixed ingredient lists on those recipes and buildings, never by restricting a
stuff category globally: plasteel walls and durasteel armor stay legal, just poor choices.

## 5. Build duties (`CANON_MATERIALS_BUILD_1`)

1. `RSW_Durasteel` def and the donor conversion of §3.2, with both recipe audits: fixed `Plasteel` costs stay
   where the consumer needs plasteel; only identified durasteel references are redirected; broad ingredient
   filters that admit both are checked separately.
2. Plasteel: remove every crafting route; patch Odyssey's asteroid generation (§3.3).
3. Salvage yields by composition for durasteel, plasteel, duranium and doonium.
4. Trade-only goods: `RSW_Phrik`, `RSW_Transparisteel`, `RSW_Stygium`, `RSW_Coaxium` defs, trader and Bazaar
   stock, stygium donor conversion.
5. Key-job exclusivity (§4), after the owner confirms the list.
6. A Mod Settings toggle for key-job exclusivity (default on), per the every-mod-ships-settings rule.
