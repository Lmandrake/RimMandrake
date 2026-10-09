# CANON_MATERIALS_DESIGN_1 — canon Star Wars materials: what they are for and where they come from

2026-10-09. **Draft for the owner's review.** Nothing here is ruled except the lines marked RULED.
Item: `CANON_MATERIALS_DESIGN_1` (parent `MINERALS_WHERE_THEY_BELONG_1`). Placement numbers live in
`design/RimMandrake/mineral_abundance_registry_2026-10-03.csv`; this doc decides *roles* and *channels*,
the registry carries the amounts.

## 0. What is already ruled (do not reopen)

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

**Durasteel** is no longer anyone's rename target, so it needs **one** canonical def. Three dispositions:

| | keep | `OuterRim_Durasteel` | `LKDurasteel_Ore` | `KOTOR_MineableDurasteel` |
|---|---|---|---|---|
| **(a) consolidate on ours** | `KOTOR_AlloyDurasteel` (Armoury, ours, already stuff with slag, smelt and ship-chunk chain) | conversion recipe 1:1 into ours; its deep/mining producers zeroed; its recipes redirected | retires with its mod (registry already retires LK Mineable Outer Rim) | zeroed, or re-used as the zersium vein if local ore is chosen (Q4) |
| **(b) new `RSW_Durasteel`** | a fresh def in the canon tier, `RSW_` per the naming grammar | conversion recipe | retires with its mod | zeroed |
| **(c) leave as found** | all three donors stay; only mining stops | stays | stays until its mod goes | zeroed |

(a) is the least work and keeps saves loading; (b) is the cleanest name but migrates `KOTOR_AlloyDurasteel`
too (four defs instead of three); (c) leaves two "durasteel" stacks side by side and is listed only so the
choice is visible. All three keep old defNames loadable until stack and save migration is done.

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
- Durasteel ends as one canonical def (§3.0); the donors stop being produced.
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

**Donor durasteels:** picks **(a)**, keep `KOTOR_AlloyDurasteel` as the one durasteel and record its prefix as
a legacy naming exception. (b) is worth it only if the canon tier must not depend on the Armoury; (c) is a
temporary compatibility state at best.

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

All six designs stay live (D1–D3 here, E1–E3 from GPT). They differ on one question only the owner can
answer: **what do materials mainly serve — building a capable colony (D1, D2, E1), being Jawas who recover
and refit (D3, E2), or trading into a wider economy (E3)?**

**Recommendation: D3's provenance identity, built with E1's assemblies.** Plasteel and durasteel are both
everyday salvage, told apart by what they rebuild: plasteel for droids, prosthetics, shields and worn
plating (Shape), durasteel for walls, blast doors, hulls and vaults (Hold), plastoid for sealed suits (Seal).
Large builds take a durasteel shell, a plasteel housing, a duranium frame and a doonium core, so all four have
a job in the same machine without competing. Plasteel comes from salvage and trade, with a costly bench recipe
only as a late fallback; never from rock or asteroids. Durasteel consolidates on `KOTOR_AlloyDurasteel`
(disposition a), `OuterRim_Durasteel` converts into it, `LKDurasteel_Ore` retires with its mod. Phrik,
transparisteel, stygium, coaxium and carbonite wait for a working consumer; quadanium folds into durasteel.

Owner questions, card-ready:
1. Base loop: build a capable colony (D1/D2/E1), recover-and-refit Jawas (D3/E2), or trade economy (E3)?
2. Durasteel's one def: keep our `KOTOR_AlloyDurasteel` (a), make a new `RSW_Durasteel` (b), or let donors coexist for now (c)?
3. Plasteel vs durasteel jobs: preferences with free choice of stuff, or exclusive (walls refuse plasteel, armor refuses durasteel)?
4. Plasteel supply: salvage and trade only, or also a costly bench recipe later?
5. Local durasteel: a zersium + steel alloy in a few industrial biomes, or salvage and trade only?
6. New materials (phrik, transparisteel, coaxium…): only once a working consumer exists, or reserve their defs now?
