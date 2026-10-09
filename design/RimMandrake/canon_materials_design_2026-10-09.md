# CANON_MATERIALS_DESIGN_1 — canon Star Wars materials: what they are for and where they come from

2026-10-09. **Draft for the owner's review.** Nothing here is ruled except the lines marked RULED.
The jobs × materials layout he asked for is `Transient/canon_materials_jobs_layout_2026-10-09.html`.
Item: `CANON_MATERIALS_DESIGN_1` (parent `MINERALS_WHERE_THEY_BELONG_1`). Placement numbers live in
`design/RimMandrake/mineral_abundance_registry_2026-10-03.csv`; this doc decides *roles* and *channels*,
the registry carries the amounts.

## 0. What is already ruled (do not reopen)

- RULED, owner typed 2026-10-09 07:05, on what materials serve: *"1+3. Having some materials only be tradable
  connects you to the greater Star Wars universe. And having a planet mining out every possible interesting
  mineral makes no sense, so salvage routes make a great deal of sense. But your comment about FOR THIS GAME,
  it's mostly about recovery, refiting, repair, and occasionally hacking together something that requires some
  of these rare materials. A planet filled with old broken salvage from massive mining companies and ANCIENT
  war fleets. And trying to make one of those ancient ships actually fly: hard enough! But then there's the
  shiny new Empire with all of its modern tech side-by-side, and you can salvage there stuff too, but the
  systems aren't greatly compatible."* ⇒ the governing loop of §0a.
- RULED 2026-10-09 by question card: durasteel becomes a **new def of ours, `RSW_Durasteel`**, and every donor
  durasteel converts into it (§3.0).
- OPEN, owner 2026-10-09 07:05, on whether material jobs are preferences or exclusive: *"Need to see the
  different jobs laid out and materials to choose from before I can get a feel for this"* — answered by the
  layout page above, not yet ruled.
- RULED, owner typed 2026-10-09: *"Apparently Plasteel is already Star Wars canon, I didn't know that, so we
  should not equate it with any other Star Wars material. Please redo the canon materials analysis you did
  but without my equivalence requirement for plasteel: let it be its own thing."* ⇒ **plasteel is its own
  canon material**, distinct from durasteel and every other canon metal.
- RULED 2026-10-03 and 2026-10-09 (cards): precious metals and gems only in their home biomes; deep drilling
  = iron everywhere, everything else by home biome.
- RULED, owner typed 2026-10-09: *"I've ruled this before. All three will exist. Duranium and Doonium are
  mostly salvage and possibly rare trade."* (2026-10-03 typed: both made offworld, pretty rare, REQUIRED to
  build large ship and machine types such as factories.)
- RULED 2026-09-25 typed: components and plasteel are never mined from rock; salvage is a major source of
  advanced materials.

## 0a. The governing loop (RULED above)

Materials in this game serve **recovery, refit and repair**, plus the **occasional hack** that needs a rare
material. Everything else follows from that:

- **Salvage routes, not planet mining.** The planet does not hold every interesting mineral. Local mines give
  the basics (iron for steel, a few home-biome ores, Lantern Deeps kyber); the advanced and rare materials are
  pulled from wrecks.
- **Trade-only materials tie the colony to the galaxy.** A small set (coaxium, aurodium, corusca, chromium)
  never appears on the planet at all: the only way to get them is a trader or the Bazaar. That is a feature,
  not a gap.
- **The rare-material hack is the peak moment.** Most work is patching things back together with durasteel,
  plasteel and components; a few repairs and refits need one stack of duranium, doonium, cortosis or beskar,
  and finding it is the expedition.
- **The flagship goal:** make one of the ancient ships actually fly. It should be hard.

### 0b. Two salvage eras

| | **Ancient** | **Imperial** |
|---|---|---|
| what it is | wrecks of massive mining companies and ANCIENT war fleets, long dead and buried | the shiny new Empire's modern tech, alive and deployed beside the old |
| where | Warscar troves, the Rust Cathedral, buried hulls, derelict mining rigs, B1 droid fields | crashed Imperial craft, outposts, patrol debris, orbital wreck salvage |
| typical yield | durasteel plate, plasteel droid shells, duranium frames, doonium reactor shielding, beskar and cortosis relics, phrik | plastoid armour, modern durasteel, plasteel housings, stygium (cloaking), transparisteel canopies, modern components |
| condition | heavily degraded; much is scrap, the rest needs restoration | mostly intact, but built to a different standard |
| canon flavour | Clone War B1s are plasteel; MagnaGuard frames are duranium; capital-ship cores are doonium-shielded | stormtrooper armour is plastoid; TIE Phantoms cloak with stygium; Death Star hull and core used doonium |

### 0c. "The systems aren't greatly compatible" — three ways to make that mechanical

Materials (durasteel, plasteel, …) are era-neutral: a plate is a plate. The incompatibility lives in
**parts** — components, assemblies, ship systems — which carry their era.

| | **I1 — Two standards + adapters** | **I2 — Mismatch penalty** | **I3 — Strip to raw** |
|---|---|---|---|
| rule | Parts come in two families (Ancient, Imperial). A machine or ship system is built to one standard and accepts only its family. Mixing needs a crafted **adapter** (bench work + a rare material, e.g. cortosis or chromium). | Mixing is allowed, but each foreign-era part in a machine adds **mismatch**: more breakdowns, lower efficiency, slower repairs. Zero mismatch = full performance. | Imperial parts cannot be installed in ancient builds at all. They are either used whole in Imperial-pattern builds, or broken down to raw materials at a reduced yield. |
| feels like | real engineering; the adapter IS the occasional rare-material hack | tinkering with a cobbled ship that mostly works | two separate economies on one planet; scrap is the bridge |
| ancient ship flight | needs ancient parts, or Imperial parts each paying for an adapter | possible with any parts, but a fully mixed ship is fragile | needs ancient parts; Imperial salvage only feeds it as raw stock |
| cost to build | two part families + adapter defs + a standard tag per consumer | one stat (mismatch) + a breakdown hook; parts still need an era tag | cheapest: deconstruction yields and recipe filters only |
| risk | doubles the component catalogue | penalty math is invisible unless surfaced in the UI | Imperial salvage may feel pointless to an ancient-ship player |

Not yet chosen; it is open question 5 in §5.

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
blunt-resistant structural alloy. The redo keeps that split and gives each a canon job. Two caveats: `Mass`
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
titles resolved with `list=search`, pulled 2026-10-09. One line of canon use, then the orthogonal ROLE
proposed for the game.

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
| **plasteel** | §2a: masks, helmet parts, greaves, blast shields, droid bodies, treads, doors, surgical bone sleeves | **Shape**: the light, formable composite — personal armor plates and shields, droid shells, prosthetics and implants, treads, light weapons. Never mined (RULED 2026-09-25) |
| **durasteel** | galaxy-wide metal alloy: armor, buildings, crates, stuncuffs, military ship plating; "more resistant than standard steel", kinetic protection; zersium ore critical to making it | **Hold**: the heavy structural alloy — walls, blast doors, hull plating, vaults, heavy turrets, crates. High HP, heavy, cheap to work |
| **beskar** | Mandalorian iron; armor that withstands blaster fire and repels lightsabers; "found only on Mandalorian worlds"; reforgeable; making weapons of it taboo to the Children of the Watch | apex *personal armor*; heirloom; never mass-produced |
| **cortosis** | extremely rare; absorbs energy (dissipates blaster bolts), can short out a lightsaber; **brittle and porous in its natural state**, useless as armor unalloyed; cortosis helmets hide the wearer's thoughts from Force users | *anti-energy / anti-Force* — shields, dampers, psychic-hiding helmets; never bulk armor |
| **phrik** | rare robust alloy, lightsaber-resistant; mined on Gromas and **Tatooine (Mos Algo mine)**; electrostaffs, Sidious's lightsabers; weaker than cortosis | *lightsaber-resistant WEAPONS* (staffs, blades) — the weapon twin of beskar's armor |
| **duranium** | tough military-grade plating, stronger than titanium, less resilient than impervium; Grievous's armor, MagnaGuard frames | *heavy frames*: large machines, war droids, factory structures (owner: required for large ship/machine types) |
| **doonium** | heavy metal used primarily for **starship construction**; Empire stockpiled it for the Death Star, essential (with dolovite) in **shielding the hypermatter reactor core**; mined on many planets and asteroid fields | *reactors and ship cores* — power plants, gravship engines/cores, radiation shielding |
| **transparisteel** | hardy transparent alloy for windows and canopies; can be blaster-proof; **lommite** ore is a major component | *see-through strong wall/window*; cockpit canopies |
| **plastoid** | armor plastic (clone and stormtrooper armor), impervious to chemical warfare, vulnerable to blaster fire | *light sealed armor* — sealed suits (tox/gas), cheap mass armor |
| **bronzium** | bronze-coloured alloy for statues, decorative finishes, some armor | *art and furniture beauty*, cheap decorative alloy |
| **aurodium** | yellow metal rarer than gold; currency standard (Cantonica), jewellery, a lightsaber hilt | *luxury / currency* metal (the galaxy's gold) |
| **chromium** | rare valuable metal; royal Naboo ship plating; reflects some radiation; chromium–titanium alloy needed in hyperdrives | *plating / prestige finish*; hyperdrive alloying |
| **quadanium** | metallic substance for ships and battle stations (Death Star hull plates, TIE wing frames), turbolasers, shields | overlaps durasteel/duranium — **candidate to fold into durasteel, not add** |
| **kyber** | Force-attuned living crystal; lightsabers; large ones at the heart of superweapons | *Force/energy focus* (already ours: Lantern Deeps only) |
| **stygium** | crystals that power cloaking devices (TIE Phantom, Scimitar) | *stealth* |
| **tibanna** | reactive gas: hyperdrives, repulsorlift coolant, fuel, **supercharges blaster bolts** | *weapon gas / coolant* (RULED: beldon herds) |
| **coaxium** | hyperfuel, rare hypermatter, mined on Kessel; raw form unstable and explodes if not kept cold | *long-range gravship fuel*; volatile cargo |
| **rhydonium** | volatile starship fuel, explosive, toxic fumes, an addictive high | *dirty fuel* + drug (already modelled) |
| **carbonite** | carbon-freezing: preserves goods and people; used to transport tibanna and coaxium | *stasis / preservation* |
| **thorilide** | prized crystal for turbolaser shock absorbers, mined with baradium | *turret component* |
| **zersium** | mineral ore essential to durasteel | *the local ore of durasteel* |
| **lommite** | ore used to make transparisteel; scattered surface deposits on a desert planetoid | *the local ore of transparisteel* |
| **dolovite** | mined on the lava worlds Mustafar and Samovar; with doonium shields reactor cores | *lava-biome mineral* |
| **corusca gem** | extremely rare valuable gemstone; smuggler's cargo | *luxury trade gem* |
| **hyperbaride** | valuable mineral on Mimban (a mud world) | *swamp-biome mineral* |
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

## 3. Three candidate designs (kept alive deliberately)

The owner's loop ruling (§0a) settles the question these designs were kept apart on: materials serve
**recovery and refit** (D3's provenance, E2's restoration), with trade-only materials as the tie to the galaxy
(E3's one surviving idea) and E1's assemblies as the way rare materials enter a build. D1 and D2 remain below
as the record of what was weighed; their per-material jobs feed the layout page.

The six origin channels every design draws from: **L** local biome mining (vein, nodule, crystal — via
the registry), **S** salvage (wrecks, Rust Cathedral, Warscar troves, crashed ships, B1 droid remains, Odyssey
orbital debris and mech-ship chunks), **A** asteroid mining (Odyssey `AsteroidMiningSite` / `Asteroid` space
maps, reached by gravship), **T** offworld trade (Bazaar, orbital traders), **H** herds/creatures (tibanna
beldons — RULED), **F** fabrication (made at a bench from other materials). Each design answers the same
two questions — what is it FOR, and where does it COME FROM — from a different first principle.

### 3.0 Plasteel and the three donor durasteels — common to all three designs

**Plasteel** keeps Core's `Plasteel` def, label and stats (§1a — already the light composite canon
describes). Its origin in every design: **S first** (crashed shuttles and ship chunks already yield it; add
B1 droid remains and droid wrecks, canon's own plasteel bodies), **T second**, and in Designs 2 and 3 a
limited **F** recipe (steel + chemfuel at the fabrication bench: a composite is *made*, not dug). **Never L,
never A**: the 2026-09-25 ruling and canon agree, and Odyssey's `MineablePlasteel` asteroid scatter is patched
out with the other rock sources.

**Durasteel is a new def of ours, `RSW_Durasteel`** (RULED by card 2026-10-09). It is canon Star Wars, so it
sits in the RimStarWars tier (`RSW_`, packageId `mandrake.rsw.*`) per `design/NAMING_SCHEME_PLAN.md`.
Starting stats: `KOTOR_AlloyDurasteel`'s (§1a — heavy, high HP, blunt- and heat-resistant), with GPT's caveat
that its sharp armor power below steel's is either raised to steel's or presented as deliberate. Every donor
durasteel converts into it:

| donor def | what happens |
|---|---|
| `KOTOR_AlloyDurasteel` (Armoury, ours) | stops being produced; its slag, smelt and ship-chunk recipes yield `RSW_Durasteel` instead; loose stacks convert 1:1 |
| `KotORChunk_durasteel`, `ShipChunk_durasteel` | their smelt/deconstruct yields point at `RSW_Durasteel` |
| `OuterRim_Durasteel` | conversion recipe 1:1; its mining and deep-drill producers zeroed; recipes that consume it redirected |
| `LKDurasteel_Ore` | ore, not alloy: measure what it is before choosing a yield; retires with its mod |
| `KOTOR_MineableDurasteel` | stops generating; kept loadable for saves. If local zersium ore is chosen (§5 Q3), that is a **new** vein, never this def repurposed |

Migration duties (GPT, §4): loose-stack conversion does not migrate built walls, worn gear, bills or saved
filters, so each donor def stays loadable — with a compatibility def shipped once its mod is retired — until
the save that carries it is replaced. Item to file when built: `RSW_DURASTEEL_CONSOLIDATION_1`.

### Design 1 — "The ladder" (a material is a TIER)

First principle: materials are a progression; the further up, the further away it comes from. Plasteel and
durasteel share tier 1 as two branches rather than one rung.

| tier | material | for | from |
|---|---|---|---|
| 0 | steel | everything basic | L (iron where the biome has it) |
| 1a | durasteel | heavy structure: walls, blast doors, vaults, turret mounts, gravship hull plating | S + T; L only as zersium ore in two or three industrial biomes, smelted |
| 1b | plasteel | light gear: armor plates, shields, droid shells, prosthetics, light weapons | S + T |
| 2 | duranium | large machines, war droids, factory buildings (owner rule) | S (crashed capital ships, mech-ship chunks), rare T |
| 3 | doonium | reactors, gravship cores/engines, big power plants | S, rare T |
| apex | beskar · cortosis · phrik | best armor · anti-energy gear · lightsaber-resistant weapons | S only (troves, Mandalorian wrecks), never mined |
| side | kyber · stygium · tibanna · coaxium | lightsabers · cloaking · blaster gas · long-range fuel | L Lantern Deeps · S · H beldons · T |

Strength: one glance tells a player what is better; easy to balance; gating is natural (a factory needs
tier 2); the 1a/1b fork teaches "heavy vs light" before the rare metals arrive. Weakness: it still collapses
toward "bigger numbers" above tier 1 — duranium vs durasteel reads as +20% rather than a different job.
Cortosis, phrik and beskar compete for the same "apex" slot.

### Design 2 — "One job each" (a material is a FUNCTION)

First principle: no two materials do the same job; every material owns one verb the game cannot do
without it, and is otherwise mediocre.

| material | owns this job | deliberately bad at | from |
|---|---|---|---|
| durasteel | **Hold** — walls, blast doors, vaults, hull plating, heavy turrets, crates | weight: worst to carry, poor for worn gear | S + T; L zersium ore (industrial biomes) |
| plasteel | **Shape** — armor plates and shields, helmets and masks, droid shells, prosthetics and implants, treads, light melee | bulk: expensive and slow to work, wasteful in walls | S + T + limited F |
| duranium | **Brace** — frames of anything bigger than a pawn: factories, big droids, turret mounts, ship hull frames | personal gear (too heavy) | S, rare T |
| doonium | **Contain** — reactor cores, gravship engine/core, radiation shielding | structure, armor | S, rare T |
| beskar | **Protect** — personal armor vs blades and bolts; reforgeable heirloom | weapons (taboo), structures | S only |
| phrik | **Parry** — weapons that resist a lightsaber (staffs, vibro-blades) | armor | L Stillsand (canon: Tatooine mine) + S |
| cortosis | **Disrupt** — energy absorption: shields, Force-dampening helmets, saber-shorting | anything raw (brittle — must be alloyed into weave) | S + T, never mined |
| transparisteel (from lommite) | **Observe** — walls you can see through: windows, canopies, observation domes | cheapness | L lommite in a desert biome, smelted with durasteel |
| plastoid | **Seal** — sealed suits and helmets (tox/gas), cheap mass armor | blaster bolts | F from chemfuel/neutroamine (no ore) |
| bronzium | **Decorate** — statues, furniture, decorative finishes | combat | F alloy / T |
| aurodium | **money and jewellery** (the galaxy's gold; currency standard) | anything practical | T, home-biome trace (precious ruling) |
| kyber | **Focus** — lightsabers, superweapon cores | — | L Lantern Deeps only (built) |
| stygium | **Conceal** — cloaking fields, invisibility gear | — | S + T |
| tibanna | **Charge** — blaster supercharge, repulsor cooling | — | H beldons (RULED) |
| coaxium | **Extend** — gravship range (hyperfuel); volatile, must be kept cold | storage | A + T, never local |
| carbonite | **Preserve** — stasis for food, prisoners, volatile cargo | — | F / T |

Strength: every material is wanted for one reason and the reason is canon; plasteel and durasteel are
opposite answers to "carry it or build with it". Weakness: 16 materials, each needing a consumer, art and
balancing — a material without a consumer is dead content.

### Design 3 — "Where it comes from IS what it is" (a material is a PROVENANCE)

First principle: the Jawa clan is a scavenger culture; origin is the gameplay, and each origin class gets a
small number of materials with a shared flavour of use.

| origin class | materials | shared use flavour |
|---|---|---|
| **Dug here** (L, per biome, registry) | zersium (→ durasteel), lommite (→ transparisteel), phrik (Stillsand), dolovite (the Forge/Pyrelands), hyperbaride (the Sump/Miasma), kyber (Lantern Deeps) | crafting inputs — the colony *makes* things from its land; each biome's ore makes that biome worth settling |
| **Pulled from wrecks** (S) | plasteel (droid bodies, shuttle panels), beskar, duranium, cortosis, durasteel plate, plastoid plate | reclaim and repurpose — gear and parts recovered and refitted; the clan's identity. Plasteel is the commonest find and the first thing a Jawa workshop reworks |
| **Made at the bench** (F) | plasteel (limited, steel + chemfuel), plastoid, bronzium, carbonite | what a settled colony learns to make for itself once it has the research |
| **Brought from orbit** (A, T) | coaxium, aurodium, corusca, chromium | the endgame — range and wealth; requires a gravship or a trader. Doonium and duranium are NOT here: they are offworld-made but recovered as S (ground and orbital wrecks) first, rare T (RULED) |
| **Grown / herded** (H) | tibanna | (already ruled) |

Strength: placement and use explain each other; the salvage identity the owner named is front and centre;
plasteel's two-origin story (salvage early, bench later) is a progression on its own. Weakness: uses are
thinner per material, and it adds several new local ores that each need a biome sitting.

### What the three share (and so is probably safe whichever wins)

- Plasteel and durasteel are **two** materials on opposite axes (Shape vs Hold, light vs heavy); neither
  converts into the other, and no recipe treats them as substitutes.
- Plasteel is never mined; it comes from salvage first and trade second.
- Durasteel ends as one canonical def, `RSW_Durasteel` (§3.0); the donors convert into it and stop being produced.
- Duranium and doonium are salvage-first, rare trade, and gate large machines/ships (owner rule).
- Beskar is salvage-only and personal-armor-only.
- Kyber stays Lantern Deeps; tibanna stays beldon herds.

## 4. GPT review (gpt-6.1-sol, high effort, 2026-10-09)

Full answer: `design/RimMandrake/canon_materials_gpt_consult_2026-10-09.md`. Its corrections already applied
above: six origin channels, not five; doonium out of D3's orbit row (salvage first, RULED); "composite" marked
as Legends; plastoid's sealing belongs to the suit, not the plate; phrik is lightsaber-*resistant*; the §1a
caveats on stack mass and stuff armor powers.

**What it says breaks in play, and the repair:**
- **Stuff eligibility.** Both are `Metallic`, so labels cannot enforce Shape vs Hold: a player can still
  build plasteel walls and wear durasteel armor. Either accept the jobs as *preferences* with generic freedom,
  or make them exclusive through fixed ingredient lists or restricted stuff categories.
- **Recipe substitution needs two audits:** fixed `Plasteel` costs stay where the consumer needs plasteel;
  only identified durasteel references are redirected; then broad ingredient filters that admit both are
  checked separately.
- **Salvage by composition, not by name.** A ship chunk can honestly yield both (durasteel plating, plasteel
  shells, components); B1 remains give plasteel once, not again through corpse processing and a wreck recipe.
  A cheap steel + chemfuel plasteel recipe would erase salvage scarcity, so any F recipe must be costly.
- **Odyssey needs an explicit allowlist** in both measured generation paths; zeroing ordinary mineable
  commonality may leave explicitly selected asteroid deposits. Orbital wreck salvage stays S, distinct from A.
- **Migration:** loose-stack conversion recipes do not migrate built walls, worn gear, bills or saved
  filters, and retiring a donor mod needs shipped compatibility defs. Do not silently repurpose
  `KOTOR_MineableDurasteel` as zersium: existing deposits would change meaning; add a new vein instead.

**Its critique of ours:** D1 should gate *projects* (duranium frame + doonium containment + durasteel
cladding + plasteel control/droid assemblies), not universal superiority. D2's exclusivity is artificial at
the edges (durasteel and duranium both claim turret mounts) and many verbs need new systems; launch only
materials with a named working consumer. D3's uses stay vague and a gravship-gated supply can block the first
gravship; guarantee a ground salvage route for first-ship needs.

**Its three designs** (common roster: steel, plasteel, durasteel, plastoid, duranium, doonium, beskar,
cortosis, kyber, tibanna, rhydonium):

| | E1 — assemblies | E2 — restoration | E3 — industrial contracts |
|---|---|---|---|
| idea | materials cooperate inside machines: durasteel outer structure, plasteel housings and droid shells, duranium frame, doonium containment | the main reward is damaged equipment: plasteel repairs droids and personal gear, durasteel repairs doors, turrets, hulls; rare materials restore relic functions | demand follows buyers: durasteel for bulk construction orders, plasteel for precision droid and prosthetic orders |
| adds | — | phrik, stygium | bronzium, aurodium |
| weakness | intermediate assemblies add bills and stockpile chores | less creative construction; needs a big damaged-item catalogue | contract tuning can turn scavenging into quota work |

**Roster advice:** fold quadanium, alusteel and ferrocarbon into durasteel's structural function. Defer
transparisteel/lommite (until windows matter), stygium (cloaking), coaxium and carbonite (fuel and
preservation systems), chromium, thorilide, dolovite. Fold hyperbaride, corusca and aurodium's wealth role
into trade rewards unless distinct demand appears. Do not promote name-only agrinium or zersium items.
**Review order only:** D3, E1, D2, E2, D1, E3.

## 5. Recommendation and what the owner decides

**Recommendation, under the ruled loop:** D3's provenance identity with E2's restoration as the main reward
and E1's assemblies for the rare-material hacks. Plasteel and durasteel are both everyday salvage, told apart
by what they rebuild: plasteel for droids, prosthetics, shields and worn plating (Shape), `RSW_Durasteel` for
walls, blast doors, hulls and vaults (Hold), plastoid for sealed suits (Seal). Large builds and ancient-ship
refits take a durasteel shell, a plasteel housing, a duranium frame and a doonium core, so all four have a job
in the same machine without competing. Coaxium, aurodium, corusca and chromium are trade-only. Phrik,
transparisteel, stygium, coaxium and carbonite wait for a working consumer; quadanium folds into durasteel.

Still open, card-ready (the layout page lists them under the matrix):
1. Plasteel and durasteel jobs: **preferences** (any metal allowed, soft penalties) or **exclusive** (walls
   refuse plasteel, armour refuses durasteel)? The owner rules after seeing the layout page.
2. Plasteel supply: salvage and trade only, or also a costly bench recipe later?
3. Durasteel supply: local zersium + steel alloy in a few industrial biomes, or salvage and trade only?
4. Unused materials (phrik, transparisteel, coaxium…): reserve their defs now, or only when something uses them?
5. Era incompatibility (§0c): I1 two standards + adapters, I2 mismatch penalty, or I3 strip to raw?
